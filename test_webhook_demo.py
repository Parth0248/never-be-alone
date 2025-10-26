"""
Quick test script for demo - tests the webhook endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:3000"

def test_audio_webhook():
    """Test the audio webhook endpoint"""
    print("\n" + "="*60)
    print("TESTING AUDIO WEBHOOK")
    print("="*60)

    payload = {
        "text": "Hello from the demo! This is a test transcription from my Omi device. Can you tell me about the weather?",
        "uid": "demo_user",
        "timestamp": datetime.now().isoformat() + "Z",
        "source": "omi_devkit_demo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/webhook/audio",
            json=payload,
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))

        return response.status_code == 200

    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

def test_health():
    """Test the health endpoint"""
    print("\n" + "="*60)
    print("TESTING HEALTH ENDPOINT")
    print("="*60)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)

        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))

        return response.status_code == 200

    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("NEVER-BE-ALONE WEBHOOK TEST")
    print("="*60)
    print(f"\nServer: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")

    # Test health
    health_ok = test_health()

    # Test audio webhook
    audio_ok = test_audio_webhook()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Health Check: {'PASS' if health_ok else 'FAIL'}")
    print(f"Audio Webhook: {'PASS' if audio_ok else 'FAIL'}")
    print("="*60)
