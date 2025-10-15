#!/usr/bin/env python3
"""
Comprehensive Workflow Test - Tests the ACTUAL User Experience

This test mimics exactly what a user would do in the frontend:
1. Load the page (fetch tools)
2. Verify SSE endpoint is available (connection test)
3. Start comprehensive analysis with async_mode=true
4. Monitor job progress via polling API
5. Verify job completes successfully with correct result structure
6. Cleanup test data

This catches integration issues that unit tests miss!
Note: SSE monitoring works great in browsers with EventSource API,
but polling is more reliable for Python tests due to stream reading timing.
"""

import time
import base64
import json
from io import BytesIO
from PIL import Image
import requests

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"


def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='blue')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def test_full_comprehensive_workflow():
    """Test complete user workflow from frontend perspective"""

    print("\n" + "="*70)
    print("COMPREHENSIVE WORKFLOW TEST")
    print("="*70 + "\n")

    # Step 1: Load frontend (fetch tools)
    print("1. Loading frontend - fetching tools...")
    response = requests.get(f"{BASE_URL}/api/tools")
    assert response.status_code == 200, f"Failed to fetch tools: {response.status_code}"
    tools = response.json()
    print(f"   ✓ Loaded {len(tools)} tools")

    # Step 2: Verify SSE endpoint is available
    print("\n2. Verifying SSE endpoint...")
    try:
        sse_response = requests.get(f"{BASE_URL}/api/jobs/stream", stream=True, timeout=5)
        if sse_response.status_code != 200:
            print(f"   ✗ SSE endpoint unavailable: {sse_response.status_code}")
            return False
        print("   ✓ SSE endpoint available")
        sse_response.close()  # Close the connection, we're just testing availability
    except Exception as e:
        print(f"   ✗ SSE endpoint check failed: {e}")
        return False

    # Step 3: Start comprehensive analysis
    print("\n3. Starting comprehensive analysis...")
    image_data = create_test_image()

    response = requests.post(
        f"{BASE_URL}/api/analyze/comprehensive?async_mode=true",
        json={
            "image": {"image_data": image_data},
            "save_as_preset": True,
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
        }
    )

    if response.status_code != 200:
        print(f"   ✗ Failed to start analysis: {response.status_code}")
        print(f"      Response: {response.text}")
        return False

    data = response.json()
    if 'job_id' not in data:
        print(f"   ✗ No job_id in response: {data}")
        return False

    job_id = data['job_id']
    print(f"   ✓ Analysis started (job_id: {job_id})")

    # Step 4: Monitor job progress via polling
    # Note: SSE works great in browsers but Python's requests library doesn't
    # start reading the stream until iter_lines() is called, which causes
    # timing issues. Polling is more reliable for testing.
    print("\n4. Monitoring job progress...")
    job_complete = False
    job_data = None
    timeout = 60  # 60 second timeout
    start_time = time.time()
    last_status = None

    while not job_complete:
        if time.time() - start_time > timeout:
            print(f"   ✗ Timeout waiting for job completion")
            return False

        # Poll job status
        try:
            response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
            if response.status_code == 200:
                job_data = response.json()
                status = job_data.get('status')
                progress = job_data.get('progress', 0) * 100
                msg = job_data.get('progress_message', '')

                # Only print status updates when they change
                if status != last_status:
                    print(f"   → Status: {status} | Progress: {progress:.0f}% | {msg}")
                    last_status = status

                if status in ['completed', 'failed', 'cancelled']:
                    job_complete = True
                    break
            else:
                print(f"   ⚠ Failed to fetch job status: {response.status_code}")

        except Exception as e:
            print(f"   ⚠ Polling error: {e}")

        # Wait before polling again
        time.sleep(0.5)

    if not job_complete:
        print("   ✗ Job did not complete")
        return False

    if job_data.get('status') != 'completed':
        print(f"   ✗ Job failed: {job_data.get('error', 'Unknown error')}")
        return False

    print(f"   ✓ Job completed successfully")

    # Step 5: Verify result structure
    print("\n5. Verifying result structure...")
    result = job_data.get('result', {})

    if 'created_presets' not in result:
        print(f"   ✗ Missing created_presets in result")
        return False

    created_presets = result['created_presets']
    print(f"   ✓ Found {len(created_presets)} presets:")
    for preset in created_presets:
        print(f"      - {preset['name']} ({preset['type']})")

    # Step 6: Verify we can fetch the job details
    print("\n6. Fetching job details via API...")
    response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
    if response.status_code != 200:
        print(f"   ✗ Failed to fetch job details: {response.status_code}")
        return False

    job_details = response.json()
    print(f"   ✓ Job details fetched")
    print(f"      Status: {job_details['status']}")
    print(f"      Progress: {job_details['progress']*100:.0f}%")

    # Step 7: Cleanup - delete the job
    print("\n7. Cleaning up (deleting job)...")
    response = requests.delete(f"{BASE_URL}/api/jobs/{job_id}")
    if response.status_code != 200:
        print(f"   ⚠ Warning: Failed to delete job: {response.status_code}")
    else:
        print(f"   ✓ Job deleted")

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - Workflow is functioning correctly!")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = test_full_comprehensive_workflow()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
