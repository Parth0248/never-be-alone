"""
Inspect actual webhook data content
"""

import requests
import json

AUDIO_WEBHOOK_URL = "https://webhook.site/token/7d8f3163-874e-4491-a29e-b0be42902456/requests"

print("="*60)
print("INSPECTING WEBHOOK DATA")
print("="*60)

try:
    response = requests.get(AUDIO_WEBHOOK_URL, timeout=10)
    data = response.json()

    if 'data' in data and data['data']:
        # Get the most recent request
        recent_req = data['data'][0]

        print(f"\nMost Recent Request:")
        print(f"UUID: {recent_req['uuid']}")
        print(f"Method: {recent_req['method']}")
        print(f"Created: {recent_req['created_at']}")
        print(f"Size: {recent_req['size']} bytes")
        print(f"IP: {recent_req['ip']}")
        print(f"User Agent: {recent_req['user_agent']}")

        # Check content
        content = recent_req.get('content')

        print(f"\n--- RAW CONTENT ---")
        if content:
            print(content)

            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print(f"\n--- PARSED JSON ---")
                print(json.dumps(parsed, indent=2))

                # Check for segments
                if 'segments' in parsed:
                    print(f"\n--- TRANSCRIPT SEGMENTS ---")
                    for i, segment in enumerate(parsed['segments']):
                        speaker = segment.get('speaker', 'Unknown')
                        text = segment.get('text', '')
                        print(f"{i+1}. {speaker}: {text}")

            except json.JSONDecodeError:
                print("Not valid JSON")

        else:
            print("No content found")

        # Show all available requests
        print(f"\n--- ALL REQUESTS ({len(data['data'])} total) ---")
        for i, req in enumerate(data['data']):
            print(f"{i+1}. {req['created_at']} - {req['method']} - {req['size']} bytes")

except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
