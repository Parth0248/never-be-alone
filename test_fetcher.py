"""
Quick test of webhook fetcher to see available data
"""

import requests
import json

AUDIO_WEBHOOK_URL = "https://webhook.site/token/7d8f3163-874e-4491-a29e-b0be42902456/requests"
IMAGE_WEBHOOK_URL = "https://webhook.site/token/4cbaf51e-538f-4bd9-9a0b-96da59c50a62/requests"

print("="*60)
print("TESTING WEBHOOK FETCHER")
print("="*60)

# Test audio webhook
print("\n1. Fetching audio webhook data...")
try:
    response = requests.get(AUDIO_WEBHOOK_URL, timeout=10)
    print(f"Status: {response.status_code}")

    data = response.json()
    print(f"Response type: {type(data)}")

    if isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
        if 'data' in data:
            requests_data = data['data']
            print(f"Number of requests: {len(requests_data)}")
            if requests_data:
                print("\nFirst request structure:")
                first_req = requests_data[0]
                print(f"Keys: {list(first_req.keys())}")

                # Try to get content
                content = first_req.get('content') or first_req.get('text_data')
                if content:
                    print(f"\nContent preview (first 500 chars):")
                    print(str(content)[:500])

except Exception as e:
    print(f"Error: {str(e)}")

print("\n" + "="*60)

# Test image webhook
print("\n2. Fetching image webhook data...")
try:
    response = requests.get(IMAGE_WEBHOOK_URL, timeout=10)
    print(f"Status: {response.status_code}")

    data = response.json()
    print(f"Response type: {type(data)}")

    if isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
        if 'data' in data:
            requests_data = data['data']
            print(f"Number of requests: {len(requests_data)}")
            if requests_data:
                print("\nFirst request structure:")
                first_req = requests_data[0]
                print(f"Keys: {list(first_req.keys())}")

                # Try to get content
                content = first_req.get('content') or first_req.get('text_data')
                if content:
                    print(f"\nContent preview (first 500 chars):")
                    print(str(content)[:500])

except Exception as e:
    print(f"Error: {str(e)}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
