"""Storage Backend Abstraction for Job Queue

Provides pluggable storage backends for job persistence:
- InMemoryBackend: Fast, no persistence (dev/testing)
- RedisBackend: Persistent, production-ready
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from api.logging_config import get_logger

logger = get_logger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def set_job(self, job_id: str, job_data: dict):
        """Store a job"""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[dict]:
        """Retrieve a job by ID"""
        pass

    @abstractmethod
    def delete_job(self, job_id: str):
        """Delete a job"""
        pass

    @abstractmethod
    def list_jobs(self) -> List[str]:
        """List all job IDs"""
        pass

    @abstractmethod
    def exists(self, job_id: str) -> bool:
        """Check if job exists"""
        pass

    @abstractmethod
    def clear_all(self):
        """Clear all jobs (for testing)"""
        pass


class InMemoryBackend(StorageBackend):
    """In-memory storage backend (no persistence)"""

    def __init__(self):
        self.jobs: Dict[str, dict] = {}

    def set_job(self, job_id: str, job_data: dict):
        self.jobs[job_id] = job_data

    def get_job(self, job_id: str) -> Optional[dict]:
        return self.jobs.get(job_id)

    def delete_job(self, job_id: str):
        if job_id in self.jobs:
            del self.jobs[job_id]

    def list_jobs(self) -> List[str]:
        return list(self.jobs.keys())

    def exists(self, job_id: str) -> bool:
        return job_id in self.jobs

    def clear_all(self):
        self.jobs.clear()


class RedisBackend(StorageBackend):
    """Redis storage backend (persistent)"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", prefix: str = "job:"):
        """
        Initialize Redis backend

        Args:
            redis_url: Redis connection URL
            prefix: Key prefix for jobs in Redis
        """
        try:
            import redis
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.prefix = prefix
            self.pubsub_channel = "job_updates"
            # Test connection
            self.redis.ping()
            logger.info(f"Connected to Redis: {redis_url}")
        except ImportError:
            raise ImportError(
                "Redis backend requires 'redis' package. "
                "Install with: pip install redis"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def _make_key(self, job_id: str) -> str:
        """Create Redis key from job ID"""
        return f"{self.prefix}{job_id}"

    def set_job(self, job_id: str, job_data: dict):
        """Store job in Redis with JSON serialization"""
        key = self._make_key(job_id)
        # Convert datetime objects to ISO strings for JSON
        serialized = self._serialize_datetimes(job_data)
        self.redis.set(key, json.dumps(serialized))

    def get_job(self, job_id: str) -> Optional[dict]:
        """Retrieve job from Redis"""
        key = self._make_key(job_id)
        data = self.redis.get(key)
        if data:
            deserialized = json.loads(data)
            return self._deserialize_datetimes(deserialized)
        return None

    def delete_job(self, job_id: str):
        """Delete job from Redis"""
        key = self._make_key(job_id)
        self.redis.delete(key)

    def list_jobs(self) -> List[str]:
        """List all job IDs"""
        pattern = f"{self.prefix}*"
        keys = self.redis.keys(pattern)
        # Strip prefix from keys
        return [key.replace(self.prefix, "") for key in keys]

    def exists(self, job_id: str) -> bool:
        """Check if job exists in Redis"""
        key = self._make_key(job_id)
        return self.redis.exists(key) > 0

    def clear_all(self):
        """Clear all jobs (for testing)"""
        pattern = f"{self.prefix}*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    def _serialize_datetimes(self, obj):
        """Recursively convert datetime objects to ISO strings"""
        if isinstance(obj, dict):
            return {k: self._serialize_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetimes(v) for v in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    def _deserialize_datetimes(self, obj):
        """Recursively convert ISO strings back to datetime objects"""
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                # Known datetime fields
                if k in ['created_at', 'started_at', 'completed_at'] and isinstance(v, str):
                    try:
                        result[k] = datetime.fromisoformat(v)
                    except:
                        result[k] = v
                else:
                    result[k] = self._deserialize_datetimes(v)
            return result
        elif isinstance(obj, list):
            return [self._deserialize_datetimes(v) for v in obj]
        return obj

    # Pub/Sub for cross-process job notifications

    def publish_job_update(self, job_data: dict):
        """
        Publish job update to Redis pub/sub channel

        Workers call this when job status changes to notify the API server.
        """
        try:
            serialized = self._serialize_datetimes(job_data)
            message = json.dumps(serialized)
            self.redis.publish(self.pubsub_channel, message)
            logger.debug(f"Published job update: {job_data.get('job_id', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to publish job update: {e}")

    def subscribe_to_updates(self):
        """
        Subscribe to job updates from Redis pub/sub

        Returns a Redis PubSub object. Use in API server to receive updates from workers.

        Example:
            pubsub = backend.subscribe_to_updates()
            for message in pubsub.listen():
                if message['type'] == 'message':
                    job_data = json.loads(message['data'])
                    # Handle job update
        """
        try:
            pubsub = self.redis.pubsub()
            pubsub.subscribe(self.pubsub_channel)
            logger.info(f"Subscribed to job updates on channel: {self.pubsub_channel}")
            return pubsub
        except Exception as e:
            logger.error(f"Failed to subscribe to job updates: {e}")
            return None
