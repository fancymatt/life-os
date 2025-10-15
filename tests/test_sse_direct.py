#!/usr/bin/env python3
"""
Test SSE endpoint directly (bypassing nginx)
"""

import requests
import json

BASE_URL = "http://localhost:8000"  # Direct API, not nginx

print("\nTesting SSE endpoint directly...")
print(f"URL: {BASE_URL}/jobs/stream\n")

# Test with streaming
response = requests.get(f"{BASE_URL}/jobs/stream", stream=True, timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Encoding: {response.encoding}")
print("\nReceiving events:")

try:
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8') if isinstance(line, bytes) else line
            print(f"  {decoded_line}")

            # Stop after seeing the connected message
            if 'connected' in decoded_line:
                print("\n✅ Successfully received SSE connected message!")
                break
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
