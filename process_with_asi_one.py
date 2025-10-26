"""
Full Pipeline with ASI:One Integration
Processes Omi data through: Reka.AI → ASI:One → Supermemory → OMI App

With detailed logging and tracing
"""

import requests
import json
import sys
import os
import logging
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent-orchestrator'))

from src.reka_client import RekaClient
from src.omi_client import OmiClient

# Import ASI:One clients
try:
    from asi_one_agentic_client import ASIOneAgenticClient
    ASI_ONE_AVAILABLE = True
except ImportError:
    print("WARNING: ASI:One client not available")
    ASI_ONE_AVAILABLE = False

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Webhook URLs
AUDIO_WEBHOOK_URL = "https://webhook.site/token/7d8f3163-874e-4491-a29e-b0be42902456/requests"
IMAGE_WEBHOOK_URL = "https://webhook.site/token/4cbaf51e-538f-4bd9-9a0b-96da59c50a62/requests"

# Initialize clients
reka_client = RekaClient()
omi_client = OmiClient()
if ASI_ONE_AVAILABLE:
    asi_one_client = ASIOneAgenticClient()

print("="*80)
print("FULL PIPELINE WITH ASI:ONE INTEGRATION")
print("="*80)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Reka API: {'OK' if reka_client.api_key else 'X'}")
print(f"OMI API: {'OK' if omi_client.api_key else 'X'}")
print(f"ASI:One API: {'OK' if ASI_ONE_AVAILABLE and asi_one_client.api_key else 'X'}")
print("="*80)

try:
    # ============================================================
    # STEP 1: FETCH DATA FROM WEBHOOKS
    # ============================================================
    print("\n" + "="*80)
    print("STEP 1: FETCHING DATA FROM WEBHOOKS")
    print("="*80)

    logger.info("Fetching audio webhook data...")
    audio_response = requests.get(AUDIO_WEBHOOK_URL, timeout=10)
    audio_data = audio_response.json()

    audio_posts = [req for req in audio_data['data'] if req['method'] == 'POST']
    print(f"[OK] Found {len(audio_posts)} audio transcripts")
    logger.info(f"Audio transcripts: {len(audio_posts)}")

    # Collect audio segments
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

    # Build transcript
    transcript_parts = []
    for segment in all_segments:
        speaker = segment.get('speaker', 'Unknown')
        text = segment.get('text', '')
        is_user = segment.get('is_user', False)
        user_label = " (USER)" if is_user else ""
        transcript_parts.append(f"{speaker}{user_label}: {text}")

    full_transcript = "\n".join(transcript_parts)
    print(f"[OK] Transcript: {len(full_transcript)} chars, {len(all_segments)} segments")
    logger.info(f"Full transcript length: {len(full_transcript)}")

    # Fetch image data
    logger.info("Fetching image webhook data...")
    image_response = requests.get(IMAGE_WEBHOOK_URL, timeout=10)
    image_data = image_response.json()

    image_posts = [req for req in image_data['data'] if req['method'] == 'POST']
    print(f"[OK] Found {len(image_posts)} image/context entries")
    logger.info(f"Image entries: {len(image_posts)}")

    # Get images and context
    images_base64 = []
    context_overview = ""

    if image_posts:
        latest_image_req = image_posts[0]
        image_content = latest_image_req.get('content')

        if image_content:
            try:
                parsed_image = json.loads(image_content)
                photos = parsed_image.get('photos', [])
                for photo in photos:
                    if 'base64' in photo:
                        images_base64.append(photo['base64'])

                structured = parsed_image.get('structured', {})
                title = structured.get('title', '')
                overview = structured.get('overview', '')
                category = structured.get('category', '')

                context_overview = f"{title}\n\nCategory: {category}\n\n{overview}"

                print(f"[OK] Images: {len(images_base64)}")
                print(f"[OK] Context: {len(context_overview)} chars")
                logger.info(f"Images: {len(images_base64)}, Context: {len(context_overview)}")

            except json.JSONDecodeError:
                pass

    # ============================================================
    # STEP 2: PROCESS THROUGH REKA.AI (MULTIMODAL UNDERSTANDING)
    # ============================================================
    print("\n" + "="*80)
    print("STEP 2: REKA.AI MULTIMODAL PROCESSING")
    print("="*80)

    # Sample images to avoid API limits
    sample_images = images_base64[:3] if len(images_base64) > 3 else images_base64

    print(f"Input:")
    print(f"  - Images: {len(sample_images)} (sampled from {len(images_base64)})")
    print(f"  - Transcript: {len(full_transcript)} chars")
    print(f"  - Visual context: {len(context_overview)} chars")

    logger.info(f"Calling Reka.AI with {len(sample_images)} images and {len(full_transcript)} char transcript")

    reka_result = reka_client.process_omi_data(
        images_base64=sample_images,
        audio_transcript=full_transcript,
        context_overview=context_overview,
        supermemory_context=""
    )

    if not reka_result['success']:
        print(f"ERROR: Reka processing failed: {reka_result.get('error')}")
        logger.error(f"Reka failed: {reka_result.get('error')}")
        sys.exit(1)

    reka_response = reka_result['response']
    print(f"\n[OK] Reka.AI analysis complete ({len(reka_response)} chars)")
    logger.info(f"Reka response: {len(reka_response)} chars")

    print("\nReka Analysis Preview:")
    print("-" * 80)
    print(reka_response[:500] + "..." if len(reka_response) > 500 else reka_response)
    print("-" * 80)

    # ============================================================
    # STEP 3: PROCESS THROUGH ASI:ONE (AGENTIC ORCHESTRATION)
    # ============================================================
    if ASI_ONE_AVAILABLE:
        print("\n" + "="*80)
        print("STEP 3: ASI:ONE AGENTIC ORCHESTRATION")
        print("="*80)

        # Prepare enhanced prompt with Reka's understanding
        asi_one_prompt = f"""Based on the conversation and visual context, extract actionable tasks:

CONVERSATION:
{full_transcript}

VISUAL CONTEXT:
{context_overview[:500]}

REKA.AI ANALYSIS:
{reka_response[:1000]}

Identify and execute:
1. Any reminders or calendar events to create
2. Tasks or follow-ups needed
3. Information to store or retrieve
4. Actions to take

Coordinate with appropriate agents from Agentverse to handle these tasks."""

        print(f"Prompt prepared: {len(asi_one_prompt)} chars")
        logger.info(f"ASI:One prompt: {len(asi_one_prompt)} chars")

        # Call ASI:One with full context
        print("\nCalling ASI:One agentic API...")
        logger.info("Calling ASI:One process_complex_task...")

        asi_result = asi_one_client.process_complex_task(
            text=asi_one_prompt,
            images_base64=sample_images[:1] if sample_images else [],  # Include 1 image for context
            entities={
                "full_transcript": full_transcript,
                "visual_context": context_overview
            },
            intent="create_reminder",  # Based on Scenario 1
            reka_understanding={
                "enhanced_understanding": reka_response[:500],
                "entities": {}
            },
            conversation_id="demo_session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        print("\n" + "="*80)
        print("ASI:ONE RESPONSE")
        print("="*80)

        if asi_result['success']:
            print(f"[OK] Success!")
            print(f"  Model used: {asi_result.get('model_used')}")
            print(f"  Complexity score: {asi_result.get('complexity_score')}/10")
            print(f"  Session ID: {asi_result.get('session_id', '')[:16]}...")
            print(f"  Agents used: {', '.join(asi_result.get('agents_used', []))}")
            print(f"  Requires polling: {asi_result.get('requires_polling', False)}")

            logger.info(f"ASI:One success - Model: {asi_result.get('model_used')}, "
                       f"Agents: {asi_result.get('agents_used')}")

            asi_response = asi_result['response']
            print(f"\nASI:One Response ({len(asi_response)} chars):")
            print("-" * 80)
            print(asi_response)
            print("-" * 80)

            # If requires polling, poll for results
            if asi_result.get('requires_polling'):
                print("\n🔄 Agent processing asynchronously, polling for results...")
                logger.info("Polling for async agent results...")

                final_result = asi_one_client.poll_for_agent_result(
                    asi_result['conversation_id'],
                    max_attempts=12,
                    wait_seconds=5
                )

                if final_result:
                    print(f"\n[OK] Final result received:")
                    print("-" * 80)
                    print(final_result)
                    print("-" * 80)
                    asi_response = final_result
                else:
                    print("\n[WARN] Polling timeout, using initial response")

        else:
            print(f"[ERROR] ASI:One failed: {asi_result.get('error')}")
            logger.error(f"ASI:One failed: {asi_result.get('error')}")
            asi_response = reka_response  # Fallback to Reka

    else:
        print("\n[WARN] ASI:One not available, using Reka response only")
        logger.warning("ASI:One not available")
        asi_response = reka_response

    # ============================================================
    # STEP 4: SEND TO OMI APP
    # ============================================================
    print("\n" + "="*80)
    print("STEP 4: SENDING TO OMI APP")
    print("="*80)

    final_response = asi_response if ASI_ONE_AVAILABLE else reka_response

    logger.info("Sending response to OMI app...")
    omi_result = omi_client.send_response(
        response_text=final_response,
        original_context=f"Audio: {full_transcript[:200]}...\n\nScene: {context_overview[:200]}..."
    )

    if omi_result['success']:
        print("[OK] Response sent to OMI app successfully!")
        logger.info("OMI app response sent successfully")
    else:
        print(f"[ERROR] Failed to send to OMI: {omi_result.get('error')}")
        logger.error(f"OMI send failed: {omi_result.get('error')}")

    # ============================================================
    # STEP 5: CREATE MEMORY IN OMI APP
    # ============================================================
    print("\n" + "="*80)
    print("STEP 5: CREATING MEMORY IN OMI APP")
    print("="*80)

    memory_text = f"""Never-Be-Alone Analysis

SCENE:
{context_overview[:400]}

CONVERSATION:
{full_transcript[:600]}

REKA.AI INSIGHTS:
{reka_response[:600]}

{'ASI:ONE ORCHESTRATION:\n' + asi_response[:600] if ASI_ONE_AVAILABLE else ''}
"""

    logger.info("Creating memory in OMI app...")
    memory_result = omi_client.create_memories(
        text=memory_text,
        text_source="other",
        text_source_spec="never_be_alone_full_pipeline"
    )

    if memory_result['success']:
        print("[OK] Memory created in OMI app successfully!")
        logger.info("OMI memory created successfully")
    else:
        print(f"[ERROR] Failed to create memory: {memory_result.get('error')}")
        logger.error(f"OMI memory failed: {memory_result.get('error')}")

    # ============================================================
    # STEP 6: STORE IN SUPERMEMORY (TODO)
    # ============================================================
    print("\n" + "="*80)
    print("STEP 6: SUPERMEMORY STORAGE")
    print("="*80)
    print("📝 Supermemory integration: TODO (use MCP)")
    logger.info("Supermemory storage pending MCP integration")

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "="*80)
    print("PIPELINE COMPLETE - SUMMARY")
    print("="*80)
    print(f"\n[OK] Processed:")
    print(f"  - Audio segments: {len(all_segments)}")
    print(f"  - Images: {len(images_base64)}")
    print(f"  - Reka analysis: {len(reka_response)} chars")
    if ASI_ONE_AVAILABLE and asi_result['success']:
        print(f"  - ASI:One orchestration: {len(asi_response)} chars")
        print(f"  - Agents used: {', '.join(asi_result.get('agents_used', ['none']))}")
        print(f"  - Model: {asi_result.get('model_used')}")
    print(f"  - OMI app response: {'OK' if omi_result['success'] else 'FAILED'}")
    print(f"  - OMI app memory: {'OK' if memory_result['success'] else 'FAILED'}")
    print("\n" + "="*80)

    logger.info("Pipeline completed successfully")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    logger.error(f"Pipeline error: {str(e)}", exc_info=True)
    import traceback
    traceback.print_exc()
