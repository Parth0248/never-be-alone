"""Snap Spectacles Video Webhook Server.

Receives video feed from Snap Spectacles and processes through Reka.ai
"""
from flask import Flask, request, jsonify
import asyncio
import logging
from typing import Dict, Any
from reka_client import get_reka_client
from orchestrator import get_orchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/api/spectacles/video', methods=['POST'])
def receive_video():
    """Receive video from Snap Spectacles.

    Expected payload:
    - video file (multipart/form-data)
    - question (optional): What to analyze
    - audio_context (optional): Related Omi transcript
    """
    try:
        logger.info("📹 [Spectacles] Received video upload request")

        # Get video file
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video_file = request.files['video']
        video_data = video_file.read()

        # Get optional parameters
        question = request.form.get('question', 'What is happening in this video?')
        audio_context = request.form.get('audio_context')

        logger.info(f"📹 Video size: {len(video_data)} bytes")
        logger.info(f"❓ Question: {question}")
        if audio_context:
            logger.info(f"🎤 Audio context: {audio_context[:100]}...")

        # Process asynchronously
        result = asyncio.run(process_video_async(video_data, question, audio_context))

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"❌ [Spectacles] Error: {e}")
        return jsonify({"error": str(e)}), 500


async def process_video_async(video_data: bytes, question: str, audio_context: str = None) -> Dict[str, Any]:
    """Process video through Reka with decision routing.

    Flow:
    1. Upload video to Reka
    2. Ask Reka the question (with audio context)
    3. Reka decides: Simple answer OR Route to ASI:One
    4. Return result

    Args:
        video_data: Video file bytes
        question: Question to ask about video
        audio_context: Optional audio transcript from Omi

    Returns:
        Processing result
    """
    reka = get_reka_client()
    orchestrator = get_orchestrator()

    try:
        # Step 1: Upload video to Reka
        logger.info("🎥 STEP 1: Uploading video to Reka...")
        video_id = await reka.upload_video(video_data, "spectacles_feed.mp4")

        if not video_id:
            return {
                "success": False,
                "error": "Video upload failed"
            }

        logger.info(f"✅ Video uploaded: {video_id}")

        # Step 2: Ask Reka (with audio context if available)
        logger.info("🤖 STEP 2: Processing video Q&A with Reka...")
        reka_result = await reka.video_qa(
            video_id=video_id,
            question=question,
            audio_transcript=audio_context,
            stream=True
        )

        if not reka_result.get("success"):
            return {
                "success": False,
                "error": "Video Q&A failed",
                "details": reka_result
            }

        answer = reka_result.get("answer", "")
        logger.info(f"✅ Reka answer: {answer[:100]}...")

        # Step 3: Decision Logic - Does this need ASI:One?
        needs_agent = should_route_to_agents(answer, question)

        if needs_agent:
            logger.info("🗺️  STEP 3: Complex task detected - routing to ASI:One...")

            # Create enriched context for agents
            enriched_context = {
                "video_id": video_id,
                "audio_context": audio_context,
                "visual_context": answer,  # Reka's understanding
                "question": question,
                "source": "snap_spectacles"
            }

            # Route to orchestrator for agentic workflow
            agent_result = await orchestrator.process_transcription(
                transcription=f"{question}\n\nVisual context: {answer}",
                context=enriched_context
            )

            return {
                "success": True,
                "type": "agent_workflow",
                "reka_understanding": answer,
                "video_id": video_id,
                "agent_result": agent_result
            }
        else:
            logger.info("✅ STEP 3: Simple query - Reka answered directly")

            return {
                "success": True,
                "type": "direct_answer",
                "answer": answer,
                "video_id": video_id,
                "reka_confidence": reka_result.get("confidence")
            }

    except Exception as e:
        logger.error(f"❌ Video processing error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def should_route_to_agents(reka_answer: str, question: str) -> bool:
    """Decide if this needs agent workflows or if Reka can handle it.

    Args:
        reka_answer: Reka's answer to the question
        question: Original question

    Returns:
        True if needs agents, False if Reka handled it
    """
    # Simple heuristics - can be enhanced with ML
    agent_keywords = [
        "remind me", "schedule", "create", "send", "book",
        "order", "buy", "set reminder", "add to calendar",
        "email", "message", "call", "search for"
    ]

    question_lower = question.lower()

    for keyword in agent_keywords:
        if keyword in question_lower:
            logger.info(f"🎯 Detected agent keyword: {keyword}")
            return True

    # Check if Reka's answer suggests action needed
    action_indicators = [
        "would you like me to", "should i", "i can help",
        "create", "schedule", "set up"
    ]

    answer_lower = reka_answer.lower()
    for indicator in action_indicators:
        if indicator in answer_lower:
            logger.info(f"🎯 Reka suggests action: {indicator}")
            return True

    # Default: Simple Q&A
    return False


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "spectacles-webhook"}), 200


if __name__ == '__main__':
    logger.info("🚀 Starting Snap Spectacles Webhook Server...")
    logger.info("📹 Endpoint: POST /api/spectacles/video")
    logger.info("🔊 Supports audio context from Omi device")
    logger.info("🤖 Routes to ASI:One for complex tasks")
    app.run(host='0.0.0.0', port=5000, debug=True)
