"""
Feature Flags Service

Simple Redis-based feature flags system for gradual rollout and A/B testing.
Supports:
- Boolean flags (enabled/disabled)
- Percentage rollout (e.g., 10% of users)
- User-specific overrides
- Default values if Redis unavailable

Usage:
    from api.services.feature_flags import get_feature_flags, check_flag

    flags = get_feature_flags()
    if flags.is_enabled("use_postgresql_backend"):
        # Use PostgreSQL
    else:
        # Use JSON files

    # Check for specific user
    if flags.is_enabled_for_user("use_postgresql_backend", user_id="user123"):
        # Enable for this specific user
"""

import redis
import json
import hashlib
from typing import Dict, Any, Optional
from functools import lru_cache

from api.logging_config import get_logger

logger = get_logger(__name__)


class FeatureFlags:
    """Feature flags manager using Redis backend"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize feature flags manager

        Args:
            redis_client: Redis client (optional, will create if not provided)
        """
        self.redis_client = redis_client
        self.prefix = "feature_flag:"

        # Default flag values (used if Redis unavailable)
        self.defaults = {
            "use_postgresql_backend": True,  # Database migration complete
            "enable_local_llm": True,  # Local LLM integration enabled
            "enable_story_workflow": True,  # Story generation workflow
            "enable_batch_operations": False,  # Batch CRUD operations (future)
            "enable_api_v2": False,  # API v2 endpoints (future)
            "strict_auth_required": False,  # Require auth for all endpoints
        }

    def _get_redis(self) -> Optional[redis.Redis]:
        """Get Redis client, create if needed"""
        if self.redis_client:
            return self.redis_client

        try:
            from api.services.job_queue import get_job_queue_manager
            job_manager = get_job_queue_manager()
            return job_manager.redis_client
        except Exception as e:
            logger.warning(f"Failed to get Redis client for feature flags: {e}")
            return None

    def is_enabled(self, flag_name: str, default: Optional[bool] = None) -> bool:
        """
        Check if a feature flag is enabled

        Args:
            flag_name: Name of the feature flag
            default: Default value if flag not found (overrides self.defaults)

        Returns:
            True if enabled, False otherwise
        """
        redis_client = self._get_redis()

        # Try to get from Redis
        if redis_client:
            try:
                key = f"{self.prefix}{flag_name}"
                value = redis_client.get(key)

                if value is not None:
                    # Parse value (supports boolean, percentage, JSON)
                    value_str = value.decode('utf-8')

                    # Boolean values
                    if value_str.lower() in ('true', '1', 'yes', 'enabled'):
                        return True
                    if value_str.lower() in ('false', '0', 'no', 'disabled'):
                        return False

                    # Percentage rollout (e.g., "50%" means 50% of requests return True)
                    if value_str.endswith('%'):
                        try:
                            percentage = int(value_str[:-1])
                            # Use deterministic hash for consistency
                            hash_value = int(hashlib.md5(flag_name.encode()).hexdigest(), 16)
                            return (hash_value % 100) < percentage
                        except ValueError:
                            pass

                    # JSON object with config
                    try:
                        config = json.loads(value_str)
                        return config.get('enabled', False)
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                logger.warning(f"Failed to check feature flag '{flag_name}': {e}")

        # Fall back to defaults
        if default is not None:
            return default
        return self.defaults.get(flag_name, False)

    def is_enabled_for_user(self, flag_name: str, user_id: str, default: Optional[bool] = None) -> bool:
        """
        Check if a feature flag is enabled for a specific user

        Supports:
        - User-specific overrides (feature_flag:{flag_name}:user:{user_id})
        - Percentage rollout (consistent per user)

        Args:
            flag_name: Name of the feature flag
            user_id: User ID
            default: Default value if flag not found

        Returns:
            True if enabled for this user, False otherwise
        """
        redis_client = self._get_redis()

        # Check user-specific override first
        if redis_client:
            try:
                user_key = f"{self.prefix}{flag_name}:user:{user_id}"
                user_value = redis_client.get(user_key)

                if user_value is not None:
                    value_str = user_value.decode('utf-8')
                    if value_str.lower() in ('true', '1', 'yes', 'enabled'):
                        return True
                    if value_str.lower() in ('false', '0', 'no', 'disabled'):
                        return False

            except Exception as e:
                logger.warning(f"Failed to check user-specific flag '{flag_name}' for user '{user_id}': {e}")

        # Check global flag with user-specific percentage rollout
        if redis_client:
            try:
                key = f"{self.prefix}{flag_name}"
                value = redis_client.get(key)

                if value is not None:
                    value_str = value.decode('utf-8')

                    # Percentage rollout (deterministic per user)
                    if value_str.endswith('%'):
                        try:
                            percentage = int(value_str[:-1])
                            # Use user ID in hash for consistency per user
                            hash_value = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest(), 16)
                            return (hash_value % 100) < percentage
                        except ValueError:
                            pass

                    # JSON object with user-based rollout
                    try:
                        config = json.loads(value_str)
                        if 'percentage' in config:
                            percentage = config['percentage']
                            hash_value = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest(), 16)
                            return (hash_value % 100) < percentage
                        return config.get('enabled', False)
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                logger.warning(f"Failed to check feature flag '{flag_name}' for user '{user_id}': {e}")

        # Fall back to global flag
        return self.is_enabled(flag_name, default)

    def set_flag(self, flag_name: str, enabled: bool, ttl: Optional[int] = None) -> bool:
        """
        Set a feature flag value

        Args:
            flag_name: Name of the feature flag
            enabled: True to enable, False to disable
            ttl: Time-to-live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        redis_client = self._get_redis()
        if not redis_client:
            logger.error(f"Cannot set feature flag '{flag_name}': Redis unavailable")
            return False

        try:
            key = f"{self.prefix}{flag_name}"
            value = 'true' if enabled else 'false'

            if ttl:
                redis_client.setex(key, ttl, value)
            else:
                redis_client.set(key, value)

            logger.info(f"Feature flag '{flag_name}' set to {enabled}")
            return True

        except Exception as e:
            logger.error(f"Failed to set feature flag '{flag_name}': {e}")
            return False

    def set_percentage(self, flag_name: str, percentage: int, ttl: Optional[int] = None) -> bool:
        """
        Set a percentage rollout for a feature flag

        Args:
            flag_name: Name of the feature flag
            percentage: Percentage (0-100)
            ttl: Time-to-live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        redis_client = self._get_redis()
        if not redis_client:
            logger.error(f"Cannot set percentage for flag '{flag_name}': Redis unavailable")
            return False

        try:
            key = f"{self.prefix}{flag_name}"
            value = f"{percentage}%"

            if ttl:
                redis_client.setex(key, ttl, value)
            else:
                redis_client.set(key, value)

            logger.info(f"Feature flag '{flag_name}' set to {percentage}% rollout")
            return True

        except Exception as e:
            logger.error(f"Failed to set percentage for flag '{flag_name}': {e}")
            return False

    def set_user_override(self, flag_name: str, user_id: str, enabled: bool) -> bool:
        """
        Set a user-specific override for a feature flag

        Args:
            flag_name: Name of the feature flag
            user_id: User ID
            enabled: True to enable, False to disable

        Returns:
            True if successful, False otherwise
        """
        redis_client = self._get_redis()
        if not redis_client:
            logger.error(f"Cannot set user override for flag '{flag_name}': Redis unavailable")
            return False

        try:
            user_key = f"{self.prefix}{flag_name}:user:{user_id}"
            value = 'true' if enabled else 'false'
            redis_client.set(user_key, value)

            logger.info(f"Feature flag '{flag_name}' set to {enabled} for user '{user_id}'")
            return True

        except Exception as e:
            logger.error(f"Failed to set user override for flag '{flag_name}': {e}")
            return False

    def get_all_flags(self) -> Dict[str, Any]:
        """
        Get all feature flags

        Returns:
            Dictionary of flag names to values
        """
        redis_client = self._get_redis()
        flags = {}

        # Start with defaults
        flags.update(self.defaults)

        # Override with Redis values
        if redis_client:
            try:
                pattern = f"{self.prefix}*"
                keys = redis_client.keys(pattern)

                for key in keys:
                    flag_name = key.decode('utf-8').replace(self.prefix, '')
                    # Skip user-specific overrides
                    if ':user:' in flag_name:
                        continue

                    value = redis_client.get(key)
                    if value:
                        value_str = value.decode('utf-8')
                        if value_str.lower() in ('true', '1', 'yes', 'enabled'):
                            flags[flag_name] = True
                        elif value_str.lower() in ('false', '0', 'no', 'disabled'):
                            flags[flag_name] = False
                        else:
                            flags[flag_name] = value_str

            except Exception as e:
                logger.warning(f"Failed to get all feature flags: {e}")

        return flags


# Singleton instance
_feature_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """Get the singleton FeatureFlags instance"""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags()
    return _feature_flags


def check_flag(flag_name: str, default: Optional[bool] = None) -> bool:
    """
    Convenience function to check a feature flag

    Args:
        flag_name: Name of the feature flag
        default: Default value if flag not found

    Returns:
        True if enabled, False otherwise
    """
    return get_feature_flags().is_enabled(flag_name, default)
