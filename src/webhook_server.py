"""
OMI Webhook Server
Receives webhooks from OMI devices (audio transcripts and images/context)
Processes them through Reka.AI and sends responses back to OMI app
"""

import os
import sys
from flask import Flask, request, jsonify
from datetime import datetime
import json
from typing import Dict, List
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom clients
from src.reka_client import RekaClient
from src.omi_client import OmiClient

load_dotenv()

app = Flask(__name__)

# Initialize clients
reka_client = RekaClient()
omi_client = OmiClient()

# Store recent data temporarily (in production, use Redis or similar)
recent_data = {
    "audio_transcripts": [],
    "image_contexts": []
}


def get_supermemory_context(query: str) -> str:
    """
    Retrieve relevant context from Supermemory

    Args:
        query: Search query

    Returns:
        Context string from Supermemory
    """
    # TODO: Implement Supermemory search via MCP
    # For now, return empty string
    return ""


def process_combined_data(audio_data: Dict, image_data: Dict) -> Dict:
    """
    Process combined audio and image data through Reka.AI

    Args:
        audio_data: Audio transcript data
        image_data: Image and context data

    Returns:
        Processing result
    """
    try:
        # Extract images (base64)
        images_base64 = []
        if 'photos' in image_data and isinstance(image_data['photos'], list):
            for photo in image_data['photos']:
                if 'base64' in photo:
                    images_base64.append(photo['base64'])

        # Extract context
        context_overview = ""
        if 'structured' in image_data:
            structured = image_data['structured']
            title = structured.get('title', '')
            overview = structured.get('overview', '')
            context_overview = f"{title}\n\n{overview}"

        # Extract audio transcript
        audio_transcript = ""
        if 'text' in audio_data:
            audio_transcript = audio_data['text']
        elif 'transcript_segments' in audio_data:
            # Combine transcript segments
            segments = audio_data['transcript_segments']
            if isinstance(segments, list):
                audio_transcript = " ".join([seg.get('text', '') for seg in segments])

        # Get context from Supermemory
        search_query = f"{context_overview[:200]} {audio_transcript[:200]}"
        supermemory_context = get_supermemory_context(search_query)

        # Process through Reka
        print(f"\nProcessing through Reka.AI...")
        print(f"   Images: {len(images_base64)}")
        print(f"   Audio transcript length: {len(audio_transcript)}")
        print(f"   Context length: {len(context_overview)}")

        reka_result = reka_client.process_omi_data(
            images_base64=images_base64,
            audio_transcript=audio_transcript,
            context_overview=context_overview,
            supermemory_context=supermemory_context
        )

        if not reka_result['success']:
            return {
                "success": False,
                "error": f"Reka processing failed: {reka_result.get('error')}"
            }

        response_text = reka_result['response']
        print(f"\nReka response received")
        print(f"   Response length: {len(response_text)}")

        # Send response to OMI app
        print(f"\nSending response to OMI app...")
        omi_result = omi_client.send_response(
            response_text=response_text,
            original_context=context_overview[:500]  # Truncate for brevity
        )

        if omi_result['success']:
            print(f"   Response sent to OMI app")
        else:
            print(f"   Failed to send to OMI: {omi_result.get('error')}")

        # Store in Supermemory
        # TODO: Implement Supermemory storage via MCP

        return {
            "success": True,
            "reka_response": response_text,
            "omi_sent": omi_result['success'],
            "images_processed": len(images_base64)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Processing error: {str(e)}"
        }


@app.route('/webhook/audio', methods=['POST'])
def webhook_audio():
    """
    Webhook endpoint for OMI audio transcripts
    """
    try:
        data = request.json
        print(f"\n" + "=" * 60)
        print(f"AUDIO WEBHOOK RECEIVED")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Store the audio data
        recent_data["audio_transcripts"].append({
            "data": data,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 10 items
        recent_data["audio_transcripts"] = recent_data["audio_transcripts"][-10:]

        # Log basic info
        if 'text' in data:
            print(f"Text length: {len(data['text'])}")

        # Check if we have recent image data to combine with
        if recent_data["image_contexts"]:
            latest_image = recent_data["image_contexts"][-1]

            # If image was received within last 60 seconds, combine them
            image_time = datetime.fromisoformat(latest_image["timestamp"])
            audio_time = datetime.now()
            time_diff = (audio_time - image_time).total_seconds()

            if time_diff < 60:
                print(f"\nCombining with recent image data (received {time_diff:.1f}s ago)")
                result = process_combined_data(data, latest_image["data"])

                return jsonify({
                    "status": "processed",
                    "combined": True,
                    "result": result
                }), 200

        # If no recent image, just acknowledge
        print(f"\nAudio data stored, waiting for image data...")

        return jsonify({
            "status": "received",
            "combined": False,
            "message": "Audio transcript received, waiting for image context"
        }), 200

    except Exception as e:
        print(f"\nError processing audio webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/webhook/images', methods=['POST'])
def webhook_images():
    """
    Webhook endpoint for OMI images and context
    """
    try:
        data = request.json
        print(f"\n" + "=" * 60)
        print(f"IMAGE WEBHOOK RECEIVED")
        print(f"=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Store the image data
        recent_data["image_contexts"].append({
            "data": data,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 10 items
        recent_data["image_contexts"] = recent_data["image_contexts"][-10:]

        # Log basic info
        if 'photos' in data:
            print(f"Images received: {len(data['photos'])}")
        if 'structured' in data and 'title' in data['structured']:
            print(f"Context: {data['structured']['title']}")

        # Check if we have recent audio data to combine with
        if recent_data["audio_transcripts"]:
            latest_audio = recent_data["audio_transcripts"][-1]

            # If audio was received within last 60 seconds, combine them
            audio_time = datetime.fromisoformat(latest_audio["timestamp"])
            image_time = datetime.now()
            time_diff = (image_time - audio_time).total_seconds()

            if time_diff < 60:
                print(f"\nCombining with recent audio data (received {time_diff:.1f}s ago)")
                result = process_combined_data(latest_audio["data"], data)

                return jsonify({
                    "status": "processed",
                    "combined": True,
                    "result": result
                }), 200

        # If no recent audio, just acknowledge
        print(f"\nImage data stored, waiting for audio data...")

        return jsonify({
            "status": "received",
            "combined": False,
            "message": "Image context received, waiting for audio transcript"
        }), 200

    except Exception as e:
        print(f"\nError processing image webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/webhook/combined', methods=['POST'])
def webhook_combined():
    """
    Webhook endpoint for combined OMI data (if both sent together)
    """
    try:
        data = request.json
        print(f"\n" + "=" * 60)
        print(f"COMBINED WEBHOOK RECEIVED")
        print(f"=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Process the combined data
        result = process_combined_data(data, data)

        return jsonify({
            "status": "processed",
            "result": result
        }), 200

    except Exception as e:
        print(f"\nError processing combined webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "reka": reka_client.api_key is not None,
            "omi": omi_client.api_key is not None
        }
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with info"""
    return jsonify({
        "service": "OMI Webhook Server",
        "version": "1.0.0",
        "endpoints": {
            "audio": "/webhook/audio",
            "images": "/webhook/images",
            "combined": "/webhook/combined",
            "health": "/health"
        },
        "status": "running"
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))

    print("=" * 60)
    print("OMI WEBHOOK SERVER STARTING")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Reka API: {'Configured' if reka_client.api_key else 'Not configured'}")
    print(f"OMI API: {'Configured' if omi_client.api_key else 'Not configured'}")
    print(f"\nEndpoints:")
    print(f"  - POST /webhook/audio - Receive audio transcripts")
    print(f"  - POST /webhook/images - Receive images and context")
    print(f"  - POST /webhook/combined - Receive combined data")
    print(f"  - GET  /health - Health check")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
