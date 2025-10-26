"""Test ASI:One API connection with the new API key."""
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

ASI_ONE_API_KEY = os.getenv('ASI_ONE_API_KEY')

print("="*80)
print("Testing ASI:One API Connection")
print("="*80)
print(f"API Key: {ASI_ONE_API_KEY[:20]}...")
print()

# Test 1: Simple chat completion
print("Test 1: Simple Chat Completion")
print("-"*80)

try:
    response = requests.post(
        "https://api.asi1.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {ASI_ONE_API_KEY}",
            "x-session-id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        },
        json={
            "model": "asi1-fast-agentic",
            "messages": [
                {"role": "user", "content": "Hello, can you help me book a flight?"}
            ],
            "stream": False
        },
        timeout=30
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS!")
        print()
        print("Response:")
        print(f"  Model: {result.get('model')}")
        print(f"  Message: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')[:200]}")

        executable_data = result.get('executable_data', {})
        if executable_data:
            print()
            print("Executable Data (Agent Discovery):")
            agent_calls = executable_data.get('agent_calls', [])
            print(f"  Agent Calls: {len(agent_calls)}")
            for i, call in enumerate(agent_calls, 1):
                print(f"    {i}. {call.get('tool_name')} (confidence: {call.get('confidence')})")

    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("="*80)

# Test 2: Intent analysis for our use case
print("Test 2: Intent Analysis for Personal Assistant")
print("-"*80)

try:
    system_prompt = """You are an intent classifier for a personal AI assistant.
Analyze the user's request and identify what they need help with."""

    response = requests.post(
        "https://api.asi1.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {ASI_ONE_API_KEY}",
            "x-session-id": str(uuid.uuid4()),
            "Content-Type": "application/json"
        },
        json={
            "model": "asi1-fast-agentic",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Remind me to call mom tomorrow at 3pm"}
            ],
            "stream": False
        },
        timeout=30
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS!")
        print()
        print("Response:")
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')
        print(f"  Analysis: {content[:300]}")

        executable_data = result.get('executable_data', {})
        if executable_data:
            print()
            print("Agent Discovery:")
            agent_calls = executable_data.get('agent_calls', [])
            for call in agent_calls:
                print(f"  - Tool: {call.get('tool_name')}")
                print(f"    Confidence: {call.get('confidence')}")
                print(f"    Arguments: {call.get('arguments', {})}")

    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("="*80)
print("Test Complete")
print("="*80)
