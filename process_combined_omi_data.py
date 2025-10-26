"""
Process Combined Omi Data (Audio + Images)
Fetches latest data from both webhooks and processes through full pipeline
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
IMAGE_WEBHOOK_URL = "https://webhook.site/token/4cbaf51e-538f-4bd9-9a0b-96da59c50a62/requests"

# Initialize clients
reka_client = RekaClient()
omi_client = OmiClient()

print("="*60)
print("PROCESSING COMBINED OMI DATA")
print("="*60)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Reka API: {'Configured' if reka_client.api_key else 'Not configured'}")
print(f"OMI API: {'Configured' if omi_client.api_key else 'Not configured'}")
print("="*60)

try:
    # Fetch audio data
    print("\n1. Fetching audio webhook data...")
    audio_response = requests.get(AUDIO_WEBHOOK_URL, timeout=10)
    audio_data = audio_response.json()

    # Filter POST requests for audio
    audio_posts = [req for req in audio_data['data'] if req['method'] == 'POST']
    print(f"   Found {len(audio_posts)} audio transcripts")

    # Collect all audio segments
    all_segments = []
    for req in audio_posts:
        content = req.get('content')
        if content:
            try:
                parsed = json.loads(content)
                segments = parsed.get('segments', [])
                all_segments.extend(segments)
            except json.JSONDecodeError:
                continue

    # Build full transcript
    transcript_parts = []
    for segment in all_segments:
        speaker = segment.get('speaker', 'Unknown')
        text = segment.get('text', '')
        is_user = segment.get('is_user', False)
        user_label = " (USER)" if is_user else ""
        transcript_parts.append(f"{speaker}{user_label}: {text}")

    full_transcript = "\n".join(transcript_parts)
    print(f"   Transcript length: {len(full_transcript)} chars")

    # Fetch image data
    print("\n2. Fetching image webhook data...")
    image_response = requests.get(IMAGE_WEBHOOK_URL, timeout=10)
    image_data = image_response.json()

    # Filter POST requests for images
    image_posts = [req for req in image_data['data'] if req['method'] == 'POST']
    print(f"   Found {len(image_posts)} image/context entries")

    # Get the most recent image post
    images_base64 = []
    context_overview = ""

    if image_posts:
        latest_image_req = image_posts[0]
        image_content = latest_image_req.get('content')

        if image_content:
            try:
                parsed_image = json.loads(image_content)

                # Extract photos
                photos = parsed_image.get('photos', [])
                for photo in photos:
                    if 'base64' in photo:
                        images_base64.append(photo['base64'])

                # Extract structured context
                structured = parsed_image.get('structured', {})
                title = structured.get('title', '')
                overview = structured.get('overview', '')
                emoji = structured.get('emoji', '')
                category = structured.get('category', '')

                context_overview = f"{title}\n\nCategory: {category}\n\n{overview}"

                print(f"   Images: {len(images_base64)}")
                print(f"   Context: {title[:50] if title else 'No title'}...")

            except json.JSONDecodeError:
                pass

    # Display what we have
    print("\n" + "="*60)
    print("DATA COLLECTED")
    print("="*60)
    print(f"\nAudio Transcript ({len(full_transcript)} chars):")
    print("-" * 60)
    print(full_transcript)
    print("-" * 60)

    if context_overview:
        print(f"\nVisual Context:")
        print("-" * 60)
        print(context_overview)
        print("-" * 60)

    # Process through Reka.AI with multimodal data
    # Limit to first 3 images to avoid API limits
    sample_images = images_base64[:3] if len(images_base64) > 3 else images_base64

    print("\n" + "="*60)
    print("PROCESSING THROUGH REKA.AI")
    print("="*60)
    print(f"Images: {len(sample_images)} (sampled from {len(images_base64)} total)")
    print(f"Transcript: {len(full_transcript)} chars")
    print(f"Context: {len(context_overview)} chars")

    reka_result = reka_client.process_omi_data(
        images_base64=sample_images,
        audio_transcript=full_transcript,
        context_overview=context_overview,
        supermemory_context=""
    )

    if not reka_result['success']:
        print(f"\nERROR: Reka processing failed: {reka_result.get('error')}")
        sys.exit(1)

    response_text = reka_result['response']

    print("\n" + "="*60)
    print("REKA.AI MULTIMODAL ANALYSIS")
    print("="*60)
    print(response_text)
    print("="*60)

    # Send to OMI app
    print("\nSending response to OMI app...")
    omi_result = omi_client.send_response(
        response_text=response_text,
        original_context=f"Audio: {full_transcript[:200]}...\n\nScene: {context_overview[:200]}..."
    )

    if omi_result['success']:
        print("SUCCESS: Response sent to OMI app!")
    else:
        print(f"WARNING: Failed to send to OMI: {omi_result.get('error')}")

    # Create memory
    print("\nCreating memory in OMI app...")
    memory_text = f"""Multimodal Analysis from Never-Be-Alone

Scene: {context_overview[:500]}

Conversation: {full_transcript[:500]}

AI Analysis:
{response_text[:1000]}
"""

    memory_result = omi_client.create_memories(
        text=memory_text,
        text_source="other",
        text_source_spec="never_be_alone_multimodal"
    )

    if memory_result['success']:
        print("SUCCESS: Memory created in OMI app!")
    else:
        print(f"WARNING: Failed to create memory: {memory_result.get('error')}")

    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"\nProcessed:")
    print(f"  - {len(all_segments)} audio segments")
    print(f"  - {len(images_base64)} images")
    print(f"  - {len(response_text)} char AI response")
    print(f"  - Sent to OMI app: {omi_result['success']}")
    print(f"  - Memory created: {memory_result['success']}")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
