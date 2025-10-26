"""
Process existing Omi data from webhook.site
One-time processing of the recorded data
"""

import requests
import json
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.reka_client import RekaClient
from src.omi_client import OmiClient

# Webhook URLs
AUDIO_WEBHOOK_URL = "https://webhook.site/token/7d8f3163-874e-4491-a29e-b0be42902456/requests"

# Initialize clients
reka_client = RekaClient()
omi_client = OmiClient()

print("="*60)
print("PROCESSING EXISTING OMI DATA")
print("="*60)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Reka API: {'Configured' if reka_client.api_key else 'Not configured'}")
print(f"OMI API: {'Configured' if omi_client.api_key else 'Not configured'}")
print("="*60)

try:
    # Fetch all requests
    print("\nFetching webhook data...")
    response = requests.get(AUDIO_WEBHOOK_URL, timeout=10)
    data = response.json()

    # Filter POST requests
    post_requests = [req for req in data['data'] if req['method'] == 'POST']
    print(f"Found {len(post_requests)} POST requests with audio transcripts")

    if not post_requests:
        print("No POST requests found with data")
        sys.exit(0)

    # Collect all transcripts
    all_segments = []
    session_ids = set()

    print("\nCollecting transcripts...")
    for req in post_requests:
        content = req.get('content')
        if content:
            try:
                parsed = json.loads(content)
                segments = parsed.get('segments', [])
                session_id = parsed.get('session_id')

                all_segments.extend(segments)
                if session_id:
                    session_ids.add(session_id)

            except json.JSONDecodeError:
                continue

    print(f"Collected {len(all_segments)} segments from {len(session_ids)} sessions")

    # Build full transcript
    transcript_parts = []
    for segment in all_segments:
        speaker = segment.get('speaker', 'Unknown')
        text = segment.get('text', '')
        is_user = segment.get('is_user', False)
        user_label = " (USER)" if is_user else ""
        transcript_parts.append(f"{speaker}{user_label}: {text}")

    full_transcript = "\n".join(transcript_parts)

    print("\n" + "="*60)
    print("FULL CONVERSATION TRANSCRIPT")
    print("="*60)
    print(full_transcript)
    print("="*60)

    # Process through Reka.AI
    print("\nProcessing through Reka.AI...")
    print(f"Transcript length: {len(full_transcript)} characters")

    reka_result = reka_client.process_omi_data(
        images_base64=[],
        audio_transcript=full_transcript,
        context_overview="Conversation recorded via Omi pendant",
        supermemory_context=""
    )

    if not reka_result['success']:
        print(f"ERROR: Reka processing failed: {reka_result.get('error')}")
        sys.exit(1)

    response_text = reka_result['response']

    print("\n" + "="*60)
    print("REKA.AI RESPONSE")
    print("="*60)
    print(response_text)
    print("="*60)

    # Send to OMI app
    print("\nSending response to OMI app...")
    omi_result = omi_client.send_response(
        response_text=response_text,
        original_context=full_transcript[:500]
    )

    if omi_result['success']:
        print("SUCCESS: Response sent to OMI app!")
    else:
        print(f"WARNING: Failed to send to OMI: {omi_result.get('error')}")

    # Also create a memory
    print("\nCreating memory in OMI app...")
    memory_result = omi_client.create_memories(
        text=f"Conversation Summary:\n{response_text}\n\nOriginal Transcript:\n{full_transcript[:1000]}",
        text_source="other",
        text_source_spec="never_be_alone_processing"
    )

    if memory_result['success']:
        print("SUCCESS: Memory created in OMI app!")
    else:
        print(f"WARNING: Failed to create memory: {memory_result.get('error')}")

    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
