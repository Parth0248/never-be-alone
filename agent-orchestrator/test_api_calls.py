#!/usr/bin/env python3
"""Test raw API calls to Reka and ASI:One to verify they're working"""
import os
import requests
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

REKA_API_KEY = os.getenv('REKA_API_KEY')
ASI_ONE_API_KEY = os.getenv('ASI_ONE_API_KEY')

async def test_reka_api():
    """Test Reka.ai API directly"""
    print("\n" + "="*80)
    print("TEST: Reka.ai API Direct Call")
    print("="*80)

    url = "https://api.reka.ai/chat"

    # Try the format we're using
    payload_v1 = {
        "model_name": "reka-flash",
        "conversation_history": [
            {
                "type": "human",
                "text": "What is 2+2?"
            }
        ]
    }

    headers = {
        "X-Api-Key": REKA_API_KEY,
        "Content-Type": "application/json"
    }

    print(f"URL: {url}")
    print(f"Model: reka-flash")
    print(f"API Key: {REKA_API_KEY[:20]}...")
    print(f"\nPayload v1 (our current format):")
    print(payload_v1)
    print(f"\nCalling API...")

    try:
        async with httpx.AsyncClient(verify=False) as client:  # Disable SSL verification for testing
            response = await client.post(url, headers=headers, json=payload_v1, timeout=30.0)
            print(f"\n[v1] Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"[v1] SUCCESS!")
                print(f"Response keys: {data.keys()}")
                if 'responses' in data:
                    content = str(data['responses'][0]['message']['content'][:100])
                    print(f"Response text: {content.encode('ascii', 'ignore').decode('ascii')}...")
            else:
                error_text = str(response.text[:200]).encode('ascii', 'ignore').decode('ascii')
                print(f"[v1] FAILED: {error_text}")
    except Exception as e:
        print(f"[v1] ERROR: {e}")

    # Try OpenAI-compatible format
    payload_v2 = {
        "messages": [
            {"role": "user", "content": "What is 2+2?"}
        ],
        "model": "reka-flash"
    }

    print(f"\n\nPayload v2 (OpenAI-compatible format):")
    print(payload_v2)
    print(f"\nCalling API...")

    try:
        async with httpx.AsyncClient(verify=False) as client:  # Disable SSL verification for testing
            response = await client.post(url, headers=headers, json=payload_v2, timeout=30.0)
            print(f"\n[v2] Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"[v2] SUCCESS!")
                response_str = str(data).encode('ascii', 'ignore').decode('ascii')
                print(f"Response: {response_str[:500]}")
            else:
                error_text = str(response.text[:200]).encode('ascii', 'ignore').decode('ascii')
                print(f"[v2] FAILED: {error_text}")
    except Exception as e:
        print(f"[v2] ERROR: {e}")


def test_asi_one_simple():
    """Test ASI:One simple chat completions API"""
    print("\n" + "="*80)
    print("TEST: ASI:One Simple Chat Completions API")
    print("="*80)

    url = "https://api.asi1.ai/v1/chat/completions"

    payload = {
        "model": "asi1-fast",  # Try non-agentic model
        "messages": [
            {"role": "user", "content": "What is 2+2?"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {ASI_ONE_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"URL: {url}")
    print(f"Model: asi1-fast (non-agentic)")
    print(f"API Key: {ASI_ONE_API_KEY[:20]}...")
    print(f"\nPayload:")
    print(payload)
    print(f"\nCalling API...")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        print(f"\nStatus: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS!")
            response_str = str(data).encode('ascii', 'ignore').decode('ascii')
            print(f"Response: {response_str[:500]}")
        else:
            error_text = str(response.text[:500]).encode('ascii', 'ignore').decode('ascii')
            print(f"FAILED: {error_text}")
    except requests.exceptions.Timeout:
        print(f"TIMEOUT: Request took longer than 30 seconds")
    except Exception as e:
        print(f"ERROR: {e}")


def test_asi_one_agentic():
    """Test ASI:One agentic API"""
    print("\n" + "="*80)
    print("TEST: ASI:One Agentic API")
    print("="*80)

    url = "https://api.asi1.ai/v1/chat/completions"

    payload = {
        "model": "asi1-fast-agentic",
        "messages": [
            {"role": "user", "content": "What is 2+2?"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {ASI_ONE_API_KEY}",
        "Content-Type": "application/json",
        "x-session-id": "test-session-123"
    }

    print(f"URL: {url}")
    print(f"Model: asi1-fast-agentic")
    print(f"API Key: {ASI_ONE_API_KEY[:20]}...")
    print(f"\nPayload:")
    print(payload)
    print(f"\nCalling API...")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60, verify=False)
        print(f"\nStatus: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS!")
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            content_ascii = content[:200].encode('ascii', 'ignore').decode('ascii')
            print(f"Response ({len(content)} chars): {content_ascii}...")
        else:
            error_text = str(response.text[:500]).encode('ascii', 'ignore').decode('ascii')
            print(f"FAILED: {error_text}")
    except requests.exceptions.Timeout:
        print(f"TIMEOUT: Request took longer than 60 seconds")
    except Exception as e:
        print(f"ERROR: {e}")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("API CONNECTIVITY TEST SUITE")
    print("="*80)

    # Test Reka
    await test_reka_api()

    # Test ASI:One Simple
    test_asi_one_simple()

    # Test ASI:One Agentic
    test_asi_one_agentic()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
