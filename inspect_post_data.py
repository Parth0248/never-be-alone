"""
Inspect POST request data from webhook
"""

import requests
import json

AUDIO_WEBHOOK_URL = "https://webhook.site/token/7d8f3163-874e-4491-a29e-b0be42902456/requests"

print("="*60)
print("INSPECTING POST REQUESTS")
print("="*60)

try:
    response = requests.get(AUDIO_WEBHOOK_URL, timeout=10)
    data = response.json()

    if 'data' in data and data['data']:
        # Filter to POST requests only
        post_requests = [req for req in data['data'] if req['method'] == 'POST']

        print(f"\nFound {len(post_requests)} POST requests")

        if post_requests:
            # Get the most recent POST
            recent_post = post_requests[0]

            print(f"\nMost Recent POST Request:")
            print(f"UUID: {recent_post['uuid']}")
            print(f"Created: {recent_post['created_at']}")
            print(f"Size: {recent_post['size']} bytes")
            print(f"User Agent: {recent_post['user_agent']}")

            # Check content
            content = recent_post.get('content')

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
                        full_transcript = []
                        for i, segment in enumerate(parsed['segments']):
                            speaker = segment.get('speaker', 'Unknown')
                            text = segment.get('text', '')
                            is_user = segment.get('is_user', False)
                            user_label = " (USER)" if is_user else ""
                            print(f"{i+1}. {speaker}{user_label}: {text}")
                            full_transcript.append(f"{speaker}: {text}")

                        print(f"\n--- FULL TRANSCRIPT ---")
                        print("\n".join(full_transcript))

                        print(f"\n--- SESSION INFO ---")
                        print(f"Session ID: {parsed.get('session_id')}")

                except json.JSONDecodeError:
                    print("Not valid JSON")

            else:
                print("No content found")

except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
