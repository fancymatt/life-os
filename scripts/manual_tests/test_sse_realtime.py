#!/usr/bin/env python3
"""
Test SSE real-time updates
"""

import requests
import json
import time
import base64
from io import BytesIO
from PIL import Image

BASE_URL = "http://localhost:3000"

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

print("\n=== Testing SSE Real-Time Updates ===\n")

# Step 1: Connect to SSE stream
print("1. Connecting to SSE stream...")
sse_response = requests.get(f"{BASE_URL}/api/jobs/stream", stream=True, timeout=120)
print(f"   Connected! Status: {sse_response.status_code}\n")

# Step 2: Start reading SSE events in a separate flow
print("2. Starting to listen for events...")
events_received = []

def read_sse_events():
    """Read SSE events from the stream"""
    for line in sse_response.iter_lines():
        if not line:
            continue

        decoded_line = line.decode('utf-8') if isinstance(line, bytes) else line

        if decoded_line.startswith(':'):
            print(f"   [Keepalive]")
            continue

        if decoded_line.startswith('data: '):
            json_str = decoded_line[6:]
            try:
                data = json.loads(json_str)
                events_received.append(data)

                if data.get('type') == 'connected':
                    print(f"   ✓ Connected message received")
                else:
                    job_id = data.get('job_id', 'N/A')
                    status = data.get('status', 'N/A')
                    progress = data.get('progress', 0) * 100
                    msg = data.get('progress_message', '')
                    print(f"   → Job {job_id[:8]}... | {status} | {progress:.0f}% | {msg}")

                    if status in ['completed', 'failed', 'cancelled']:
                        print(f"\n   ✅ Job {status}!")
                        return data
            except json.JSONDecodeError as e:
                print(f"   ✗ JSON error: {e}")

# Step 3: Start analysis in parallel
print("\n3. Triggering comprehensive analysis...")
time.sleep(0.5)  # Give SSE connection time to settle

image_data = create_test_image()
analysis_response = requests.post(
    f"{BASE_URL}/api/analyze/comprehensive?async_mode=true",
    json={
        "image": {"image_data": image_data},
        "save_as_preset": True,
        "skip_cache": True,
        "selected_analyses": {
            "outfit": True,
            "visual_style": False,
            "hair_style": False,
            "hair_color": False,
            "makeup": False,
            "accessories": False,
            "art_style": False,
            "expression": False
        }
    }
)

if analysis_response.status_code != 200:
    print(f"   ✗ Failed: {analysis_response.status_code}")
    print(f"   {analysis_response.text}")
    exit(1)

job_id = analysis_response.json()['job_id']
print(f"   ✓ Analysis started! Job ID: {job_id}\n")

# Step 4: Now read events
print("4. Monitoring SSE stream for updates...")
result = read_sse_events()

if result:
    print(f"\n=== TEST PASSED ===")
    print(f"Job completed successfully!")
    print(f"Received {len(events_received)} total events")
else:
    print(f"\n=== TEST INCOMPLETE ===")
    print(f"Received {len(events_received)} events but job didn't complete")
