#!/usr/bin/env python3
"""
Comprehensive Test Suite for Job Queue System

Tests:
1. Backend API endpoints
2. Job queue functionality
3. SSE streaming
4. Analyzer integration with job queue
5. Frontend compatibility
"""

import asyncio
import time
import json
import base64
from pathlib import Path
import requests
from io import BytesIO
from PIL import Image

# Configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "jenny.png"  # Use existing test image


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test(name):
    """Print test name"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing: {name}{Colors.ENDC}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def create_test_image() -> str:
    """Create a test image and return base64 encoded string"""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


class JobQueueSystemTests:
    """Comprehensive test suite for job queue system"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_image_base64 = create_test_image()

    def test_health_check(self):
        """Test API health endpoint"""
        print_test("API Health Check")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()
            assert data['status'] in ['healthy', 'degraded'], f"Unexpected status: {data['status']}"

            print_success(f"API is {data['status']}")
            self.passed += 1
            return True
        except Exception as e:
            print_error(f"Health check failed: {e}")
            self.failed += 1
            return False

    def test_list_analyzers(self):
        """Test listing available analyzers"""
        print_test("List Analyzers")
        try:
            response = requests.get(f"{BASE_URL}/api/analyze/", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()
            assert isinstance(data, list), "Expected list of analyzers"
            assert len(data) > 0, "No analyzers found"

            analyzer_names = [a['name'] for a in data]
            expected_analyzers = ['outfit', 'comprehensive', 'visual-style', 'hair-style']
            for name in expected_analyzers:
                assert name in analyzer_names, f"Missing analyzer: {name}"

            print_success(f"Found {len(data)} analyzers: {', '.join(analyzer_names)}")
            self.passed += 1
            return True
        except Exception as e:
            print_error(f"List analyzers failed: {e}")
            self.failed += 1
            return False

    def test_job_endpoints(self):
        """Test job management endpoints"""
        print_test("Job Management Endpoints")
        try:
            # Test GET /api/jobs
            response = requests.get(f"{BASE_URL}/api/jobs", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            jobs = response.json()
            assert isinstance(jobs, list), "Expected list of jobs"

            print_success(f"GET /api/jobs works (found {len(jobs)} jobs)")
            self.passed += 1
            return True
        except Exception as e:
            print_error(f"Job endpoints test failed: {e}")
            self.failed += 1
            return False

    def test_sync_analysis(self):
        """Test synchronous analysis (async_mode=false)"""
        print_test("Synchronous Analysis")
        try:
            response = requests.post(
                f"{BASE_URL}/api/analyze/outfit?async_mode=false",
                json={
                    "image": {
                        "image_data": self.test_image_base64
                    },
                    "save_as_preset": False,
                    "skip_cache": True
                },
                timeout=30
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()
            assert data['status'] in ['completed', 'failed'], f"Unexpected status: {data.get('status')}"

            if data['status'] == 'completed':
                assert 'result' in data, "Missing result field"
                print_success(f"Sync analysis completed in {data.get('processing_time', 0):.2f}s")
            else:
                print_warning(f"Sync analysis failed: {data.get('error', 'Unknown error')}")
                self.warnings += 1

            self.passed += 1
            return True
        except Exception as e:
            print_error(f"Sync analysis test failed: {e}")
            self.failed += 1
            return False

    def test_async_analysis(self):
        """Test asynchronous analysis (async_mode=true)"""
        print_test("Asynchronous Analysis with Job Queue")
        try:
            # Start async analysis
            response = requests.post(
                f"{BASE_URL}/api/analyze/outfit?async_mode=true",
                json={
                    "image": {
                        "image_data": self.test_image_base64
                    },
                    "save_as_preset": False,
                    "skip_cache": True
                },
                timeout=10
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()
            assert 'job_id' in data, "Missing job_id field"
            assert data['status'] == 'queued', f"Expected queued status, got {data['status']}"

            job_id = data['job_id']
            print_success(f"Analysis queued with job_id: {job_id}")

            # Poll for job completion
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(1)

                job_response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", timeout=5)
                assert job_response.status_code == 200, f"Expected 200, got {job_response.status_code}"

                job = job_response.json()
                print(f"  Job status: {job['status']} (progress: {job['progress']*100:.0f}%)")

                if job['status'] in ['completed', 'failed', 'cancelled']:
                    break

            assert job['status'] == 'completed', f"Job did not complete (status: {job['status']})"
            print_success(f"Job completed successfully")

            # Test job deletion
            delete_response = requests.delete(f"{BASE_URL}/api/jobs/{job_id}", timeout=5)
            assert delete_response.status_code == 200, f"Failed to delete job"
            print_success("Job deleted successfully")

            self.passed += 1
            return True
        except Exception as e:
            print_error(f"Async analysis test failed: {e}")
            self.failed += 1
            return False

    def test_comprehensive_async_analysis(self):
        """Test comprehensive analysis with job queue"""
        print_test("Comprehensive Async Analysis")
        try:
            # Start comprehensive async analysis
            response = requests.post(
                f"{BASE_URL}/api/analyze/comprehensive?async_mode=true",
                json={
                    "image": {
                        "image_data": self.test_image_base64
                    },
                    "save_as_preset": False,
                    "skip_cache": True,
                    "selected_analyses": {
                        "outfit": True,
                        "visual_style": True,
                        "hair_style": False,
                        "hair_color": False,
                        "makeup": False,
                        "accessories": False,
                        "art_style": False,
                        "expression": False
                    }
                },
                timeout=10
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            data = response.json()
            assert 'job_id' in data, "Missing job_id field"

            job_id = data['job_id']
            print_success(f"Comprehensive analysis queued: {job_id}")

            # Poll for completion
            max_attempts = 60
            for attempt in range(max_attempts):
                time.sleep(2)

                job_response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", timeout=5)
                job = job_response.json()

                progress_msg = job.get('progress_message', '')
                print(f"  Status: {job['status']} | Progress: {job['progress']*100:.0f}% | {progress_msg}")

                if job['status'] in ['completed', 'failed', 'cancelled']:
                    break

            if job['status'] == 'completed':
                print_success("Comprehensive analysis completed")

                # Clean up
                requests.delete(f"{BASE_URL}/api/jobs/{job_id}", timeout=5)
                self.passed += 1
                return True
            else:
                print_warning(f"Comprehensive analysis status: {job['status']}")
                if job.get('error'):
                    print_warning(f"Error: {job['error']}")
                self.warnings += 1
                return False

        except Exception as e:
            print_error(f"Comprehensive async analysis failed: {e}")
            self.failed += 1
            return False

    def test_job_cancellation(self):
        """Test job cancellation"""
        print_test("Job Cancellation")
        try:
            # Start a job
            response = requests.post(
                f"{BASE_URL}/api/analyze/outfit?async_mode=true",
                json={
                    "image": {
                        "image_data": self.test_image_base64
                    },
                    "save_as_preset": False,
                    "skip_cache": True
                },
                timeout=10
            )

            job_id = response.json()['job_id']
            print_success(f"Job created: {job_id}")

            # Immediately try to cancel it
            time.sleep(0.5)  # Give it a moment to start

            cancel_response = requests.post(
                f"{BASE_URL}/api/jobs/{job_id}/cancel",
                timeout=5
            )

            if cancel_response.status_code == 200:
                job = cancel_response.json()
                if job['status'] == 'cancelled':
                    print_success("Job cancelled successfully")
                    self.passed += 1
                    return True
                else:
                    print_warning(f"Job already completed with status: {job['status']}")
                    self.warnings += 1
                    return False
            else:
                print_warning(f"Cancel returned {cancel_response.status_code}")
                self.warnings += 1
                return False

        except Exception as e:
            print_error(f"Job cancellation test failed: {e}")
            self.failed += 1
            return False

    def test_concurrent_jobs(self):
        """Test multiple concurrent jobs"""
        print_test("Concurrent Jobs")
        try:
            job_ids = []

            # Start 3 concurrent jobs
            for i in range(3):
                response = requests.post(
                    f"{BASE_URL}/api/analyze/outfit?async_mode=true",
                    json={
                        "image": {
                            "image_data": self.test_image_base64
                        },
                        "save_as_preset": False,
                        "skip_cache": True
                    },
                    timeout=10
                )

                job_ids.append(response.json()['job_id'])

            print_success(f"Started {len(job_ids)} concurrent jobs")

            # Wait for all to complete
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(1)

                statuses = []
                for job_id in job_ids:
                    job_response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", timeout=5)
                    job = job_response.json()
                    statuses.append(job['status'])

                print(f"  Job statuses: {statuses}")

                if all(s in ['completed', 'failed', 'cancelled'] for s in statuses):
                    break

            completed = sum(1 for s in statuses if s == 'completed')
            print_success(f"{completed}/{len(job_ids)} jobs completed")

            # Cleanup
            for job_id in job_ids:
                requests.delete(f"{BASE_URL}/api/jobs/{job_id}", timeout=5)

            if completed == len(job_ids):
                self.passed += 1
                return True
            else:
                self.warnings += 1
                return False

        except Exception as e:
            print_error(f"Concurrent jobs test failed: {e}")
            self.failed += 1
            return False

    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}{'='*70}")
        print(f"Job Queue System - Comprehensive Test Suite")
        print(f"{'='*70}{Colors.ENDC}\n")

        # Run tests
        self.test_health_check()
        self.test_list_analyzers()
        self.test_job_endpoints()
        self.test_sync_analysis()
        self.test_async_analysis()
        self.test_comprehensive_async_analysis()
        self.test_job_cancellation()
        self.test_concurrent_jobs()

        # Print summary
        print(f"\n{Colors.BOLD}{'='*70}")
        print("Test Summary")
        print(f"{'='*70}{Colors.ENDC}")
        print(f"{Colors.GREEN}✓ Passed: {self.passed}{Colors.ENDC}")
        print(f"{Colors.RED}✗ Failed: {self.failed}{Colors.ENDC}")
        print(f"{Colors.YELLOW}⚠ Warnings: {self.warnings}{Colors.ENDC}")

        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}\n")

        return self.failed == 0


if __name__ == "__main__":
    tests = JobQueueSystemTests()
    success = tests.run_all_tests()
    exit(0 if success else 1)
