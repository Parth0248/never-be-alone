"""Test script to simulate Omi device sending transcriptions."""
import requests
import time

# Server URL (use ngrok URL in production, localhost for testing)
SERVER_URL = "http://localhost:8081"

print("="*80)
print("Testing Omi Webhook Integration")
print("="*80)
print(f"Server: {SERVER_URL}")
print()

# Test 1: Health Check
print("Test 1: Health Check")
print("-"*80)

try:
    response = requests.get(f"{SERVER_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("[OK] Health check passed")
except Exception as e:
    print(f"[FAIL] Health check failed: {e}")
    print("Make sure the server is running: python omi_webhook_integration.py")
    exit(1)

print()

# Test 2: Simple Transcription
print("Test 2: Send Simple Transcription")
print("-"*80)

test_data = {
    "transcription": "Remind me to call John tomorrow at 3pm",
    "uid": "test_user",
    "timestamp": "2025-10-25T15:30:00Z"
}

try:
    response = requests.post(
        f"{SERVER_URL}/omi/transcription",
        json=test_data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    if result.get("success"):
        print("[OK] Transcription processed!")
        print(f"  Intent: {result['processing_result']['intent']}")
        print(f"  Confidence: {result['processing_result']['confidence']}")
        print(f"  Actions: {result['processing_result']['actions_taken']}")
    else:
        print(f"[FAIL] {result.get('error')}")

except Exception as e:
    print(f"[FAIL] Error: {e}")

print()
time.sleep(2)

# Test 3: Segment Format (like real Omi)
print("Test 3: Send Omi Segment Format")
print("-"*80)

segment_data = {
    "session_id": "test_session_123",
    "segments": [
        {
            "text": "Schedule a team meeting",
            "speaker": "SPEAKER_00",
            "start": 0.0,
            "end": 2.5,
            "is_user": True
        },
        {
            "text": "for next Monday at 10am",
            "speaker": "SPEAKER_00",
            "start": 2.5,
            "end": 5.0,
            "is_user": True
        }
    ]
}

try:
    response = requests.post(
        f"{SERVER_URL}/omi/transcription",
        json=segment_data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    if result.get("success"):
        print("[OK] Segments processed!")
        print(f"  Combined: {result['transcription']}")
        print(f"  Intent: {result['processing_result']['intent']}")
        print(f"  Actions: {result['processing_result']['actions_taken']}")
    else:
        print(f"[FAIL] {result.get('error')}")

except Exception as e:
    print(f"[FAIL] Error: {e}")

print()
time.sleep(2)

# Test 4: Question Format
print("Test 4: Question Transcription")
print("-"*80)

question_data = {
    "text": "What did I say about the project last week?"
}

try:
    response = requests.post(
        f"{SERVER_URL}/omi/transcription",
        json=question_data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    if result.get("success"):
        print("[OK] Question processed!")
        print(f"  Intent: {result['processing_result']['intent']}")
        print(f"  Confidence: {result['processing_result']['confidence']}")
    else:
        print(f"[FAIL] {result.get('error')}")

except Exception as e:
    print(f"[FAIL] Error: {e}")

print()
print("="*80)
print("Testing Complete!")
print("="*80)
print()
print("Check webhook.site to see the results:")
print("https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9")
print()
