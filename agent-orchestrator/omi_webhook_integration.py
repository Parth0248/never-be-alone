"""Omi Device Webhook Integration - Receives live transcripts and processes them through agent orchestrator."""
import requests
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from orchestrator import get_orchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Flask app for receiving Omi webhooks
app = Flask(__name__)
CORS(app)

# Get orchestrator instance
orchestrator = get_orchestrator()

# Your webhook.site endpoint for debugging/monitoring
WEBHOOK_SITE_URL = "https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9"


def convert_datetimes(obj):
    """Convert datetime objects to ISO strings for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetimes(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes(item) for item in obj]
    return obj


def send_to_webhook_site(data: Dict[str, Any]):
    """Send data to webhook.site for monitoring.

    Args:
        data: Data to send to webhook.site
    """
    try:
        # Convert any datetime objects to strings
        serializable_data = convert_datetimes(data)
        response = requests.post(
            WEBHOOK_SITE_URL,
            json=serializable_data,
            timeout=5
        )
        logger.info(f"Sent to webhook.site: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending to webhook.site: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "omi-webhook-integration",
        "orchestrator_status": "connected",
        "agents_count": len(orchestrator.agents)
    })


@app.route('/omi/transcription', methods=['POST'])
def receive_omi_transcription():
    """Receive transcription from Omi device and process through agent orchestrator.

    Expected payload from Omi:
    {
        "session_id": "session_123",
        "segments": [
            {
                "text": "transcription text",
                "speaker": "SPEAKER_00",
                "start": 0.0,
                "end": 5.0,
                "is_user": true
            }
        ]
    }

    Or simple format:
    {
        "transcription": "text",
        "uid": "user_id",
        "timestamp": "2025-10-25T15:30:00Z"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        logger.info(f"Received Omi transcription: {data}")

        # Extract transcription text
        transcription_text = ""

        # Handle Omi segment format
        if "segments" in data:
            segments = data.get("segments", [])
            # Combine all segments into full transcription
            transcription_text = " ".join([seg.get("text", "") for seg in segments if seg.get("text")])

        # Handle simple format
        elif "transcription" in data:
            transcription_text = data.get("transcription", "")

        # Handle text field directly
        elif "text" in data:
            transcription_text = data.get("text", "")

        if not transcription_text:
            return jsonify({
                "success": False,
                "error": "No transcription text found"
            }), 400

        # Build context from Omi data
        context = {
            "uid": data.get("uid") or data.get("user_id") or data.get("session_id", "unknown"),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "source": "omi_device",
            "session_id": data.get("session_id"),
            "segments_count": len(data.get("segments", [])) if "segments" in data else 1
        }

        # Send original data to webhook.site for monitoring
        send_to_webhook_site({
            "event": "omi_transcription_received",
            "transcription": transcription_text,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

        # Process through agent orchestrator
        result = asyncio.run(
            orchestrator.process_transcription(transcription_text, context)
        )

        # Send result to webhook.site for monitoring
        send_to_webhook_site({
            "event": "agent_processing_complete",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })

        # Return success response
        response = {
            "success": True,
            "transcription": transcription_text,
            "processing_result": {
                "intent": result.get("intent"),
                "confidence": result.get("confidence"),
                "actions_taken": result.get("actions_taken"),
                "agent_count": len(result.get("results", []))
            },
            "message": "Transcription processed successfully"
        }

        logger.info(f"Processed transcription: {result.get('intent')} - {result.get('actions_taken')}")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing Omi transcription: {e}", exc_info=True)

        # Send error to webhook.site
        send_to_webhook_site({
            "event": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/omi/audio', methods=['POST'])
def receive_omi_audio():
    """Receive raw audio from Omi device (if needed for future processing).

    This endpoint can receive raw audio and trigger transcription,
    but for now we expect transcriptions to come pre-processed.
    """
    try:
        # Get audio data
        if 'audio' in request.files:
            audio_file = request.files['audio']
            logger.info(f"Received audio file: {audio_file.filename}")
        else:
            audio_data = request.data
            logger.info(f"Received raw audio data: {len(audio_data)} bytes")

        # Send notification to webhook.site
        send_to_webhook_site({
            "event": "audio_received",
            "size_bytes": len(request.data),
            "timestamp": datetime.now().isoformat(),
            "message": "Audio received - transcription processing not yet implemented"
        })

        return jsonify({
            "success": True,
            "message": "Audio received - will be processed when transcription is ready"
        }), 200

    except Exception as e:
        logger.error(f"Error receiving audio: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint to verify webhook integration is working."""
    try:
        data = request.get_json() or {}
        test_text = data.get("text", "This is a test transcription")

        # Send test to webhook.site
        send_to_webhook_site({
            "event": "test",
            "text": test_text,
            "timestamp": datetime.now().isoformat()
        })

        # Process through orchestrator
        result = asyncio.run(
            orchestrator.process_transcription(test_text, {
                "uid": "test_user",
                "source": "test_endpoint"
            })
        )

        return jsonify({
            "success": True,
            "message": "Test successful",
            "result": result
        }), 200

    except Exception as e:
        logger.error(f"Test error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    logger.info("="*80)
    logger.info("Omi Webhook Integration Server Starting")
    logger.info("="*80)
    logger.info(f"Webhook.site monitoring: {WEBHOOK_SITE_URL}")
    logger.info(f"Orchestrator agents: {list(orchestrator.agents.keys())}")
    logger.info("="*80)
    logger.info("")
    logger.info("Available endpoints:")
    logger.info("  POST /omi/transcription - Receive transcriptions from Omi")
    logger.info("  POST /omi/audio - Receive raw audio from Omi")
    logger.info("  POST /test - Test the integration")
    logger.info("  GET /health - Health check")
    # Use port 8081 to avoid conflicts
    port = 8081

    logger.info("")
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    logger.info("="*80)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
