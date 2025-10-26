"""
Omi Audio Streaming Server
Receives audio bytes from Omi wearable devices and saves them as WAV files in Google Cloud Storage.

Environment Variables Required:
- GOOGLE_APPLICATION_CREDENTIALS_JSON: Base64-encoded GCP service account credentials
- GCS_BUCKET_NAME: Name of the GCS bucket to store audio files

Reference: https://docs.omi.me/doc/developer/AudioStreaming
Based on: https://github.com/mdmohsin7/omi-audio-streaming
"""

import os
import base64
import struct
import tempfile
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from google.cloud import storage
from google.oauth2 import service_account
import json
from dotenv import load_dotenv
import requests

# Load environment variables from .dev.vars file
load_dotenv('.dev.vars')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Audio constants for Omi DevKit 2
NUM_CHANNELS = 1        # Mono audio
SAMPLE_RATE = 16000     # 16 kHz
BITS_PER_SAMPLE = 16    # 16-bit audio

# Initialize Flask app
app = Flask(__name__)


def create_wav_header(data_length: int) -> bytes:
    """
    Create a WAV file header for the given audio data length.

    WAV Format Specification:
    - Bytes 0-3: "RIFF" chunk descriptor
    - Bytes 4-7: File size - 8
    - Bytes 8-11: "WAVE" format
    - Bytes 12-15: "fmt " subchunk
    - Bytes 16-19: Subchunk size (16 for PCM)
    - Bytes 20-21: Audio format (1 for PCM)
    - Bytes 22-23: Number of channels
    - Bytes 24-27: Sample rate
    - Bytes 28-31: Byte rate
    - Bytes 32-33: Block align
    - Bytes 34-35: Bits per sample
    - Bytes 36-39: "data" subchunk
    - Bytes 40-43: Data size

    Args:
        data_length: Length of the audio data in bytes

    Returns:
        44-byte WAV header as bytes
    """
    byte_rate = SAMPLE_RATE * NUM_CHANNELS * BITS_PER_SAMPLE // 8
    block_align = NUM_CHANNELS * BITS_PER_SAMPLE // 8

    header = bytearray(44)

    # RIFF chunk descriptor
    header[0:4] = b'RIFF'
    header[4:8] = struct.pack('<I', 36 + data_length)  # File size - 8
    header[8:12] = b'WAVE'

    # fmt subchunk
    header[12:16] = b'fmt '
    header[16:20] = struct.pack('<I', 16)  # Subchunk size
    header[20:22] = struct.pack('<H', 1)   # Audio format (PCM)
    header[22:24] = struct.pack('<H', NUM_CHANNELS)
    header[24:28] = struct.pack('<I', SAMPLE_RATE)
    header[28:32] = struct.pack('<I', byte_rate)
    header[32:34] = struct.pack('<H', block_align)
    header[34:36] = struct.pack('<H', BITS_PER_SAMPLE)

    # data subchunk
    header[36:40] = b'data'
    header[40:44] = struct.pack('<I', data_length)

    return bytes(header)


def get_gcs_client():
    """
    Initialize and return a Google Cloud Storage client.

    Uses the GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable,
    which should contain base64-encoded service account credentials.

    Returns:
        storage.Client: Initialized GCS client

    Raises:
        ValueError: If environment variable is not set
        Exception: If credentials are invalid
    """
    creds_env = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not creds_env:
        raise ValueError('GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set')

    try:
        # Decode base64-encoded credentials
        creds_json = base64.b64decode(creds_env).decode('utf-8')
        creds_dict = json.loads(creds_json)

        # Create credentials object
        credentials = service_account.Credentials.from_service_account_info(creds_dict)

        # Initialize storage client
        client = storage.Client(credentials=credentials, project=creds_dict.get('project_id'))

        logger.info('Successfully initialized GCS client')
        return client

    except Exception as e:
        logger.error(f'Failed to initialize GCS client: {e}')
        raise


def upload_to_gcs(bucket_name: str, filename: str, file_path: str) -> bool:
    """
    Upload a file to Google Cloud Storage.

    Args:
        bucket_name: Name of the GCS bucket
        filename: Name to give the file in GCS
        file_path: Local path to the file to upload

    Returns:
        bool: True if upload successful, False otherwise
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(filename)

        # Upload file with content type
        blob.upload_from_filename(file_path, content_type='audio/wav')

        logger.info(f'Successfully uploaded {filename} to GCS bucket {bucket_name}')
        return True

    except Exception as e:
        logger.error(f'Failed to upload to GCS: {e}')
        return False


@app.route('/audio', methods=['POST'])
def handle_audio():
    """
    Handle POST requests with audio bytes from Omi device.

    Query Parameters:
        - uid: User identifier (required)
        - sample_rate: Audio sample rate in Hz (optional, default: 16000)

    Request Body:
        Raw audio bytes (application/octet-stream)

    Returns:
        JSON response with success status and filename
    """
    # Get query parameters
    uid = request.args.get('uid')
    sample_rate_param = request.args.get('sample_rate', '16000')

    logger.info(f'Received audio request from uid: {uid}, sample_rate: {sample_rate_param}')

    if not uid:
        return jsonify({'error': 'uid parameter is required'}), 400

    # Get environment variables
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    if not bucket_name:
        logger.error('GCS_BUCKET_NAME environment variable is not set')
        return jsonify({'error': 'Server configuration error: GCS_BUCKET_NAME not set'}), 500

    try:
        # Read audio bytes from request body
        audio_data = request.get_data()

        if not audio_data:
            return jsonify({'error': 'No audio data received'}), 400

        logger.info(f'Received {len(audio_data)} bytes of audio data')

        # Generate filename with timestamp
        now = datetime.now()
        filename = now.strftime('%d_%m_%Y_%H_%M_%S.wav')

        # Create WAV header
        wav_header = create_wav_header(len(audio_data))

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            # Write WAV header and audio data
            temp_file.write(wav_header)
            temp_file.write(audio_data)

        logger.info(f'Created temporary WAV file: {temp_path}')

        # Upload to GCS
        success = upload_to_gcs(bucket_name, filename, temp_path)

        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except Exception as e:
            logger.warning(f'Failed to delete temporary file: {e}')

        if success:
            return jsonify({
                'success': True,
                'message': f'Audio bytes received and uploaded as {filename}',
                'filename': filename,
                'uid': uid,
                'size_bytes': len(audio_data)
            }), 200
        else:
            return jsonify({
                'error': 'Failed to upload to Google Cloud Storage'
            }), 500

    except Exception as e:
        logger.error(f'Error processing audio: {e}')
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/transcription', methods=['POST'])
def handle_transcription():
    """
    Handle POST requests with transcription data from Omi device.

    Query Parameters:
        - uid: User identifier (required)

    Request Body:
        JSON with transcription text and optional metadata

    Returns:
        JSON response with success status and filename
    """
    # Get query parameters
    uid = request.args.get('uid')

    logger.info(f'Received transcription request from uid: {uid}')

    if not uid:
        return jsonify({'error': 'uid parameter is required'}), 400

    # Get environment variables
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    if not bucket_name:
        logger.error('GCS_BUCKET_NAME environment variable is not set')
        return jsonify({'error': 'Server configuration error: GCS_BUCKET_NAME not set'}), 500

    try:
        # Get JSON data from request
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data received'}), 400

        # Extract transcription text
        transcription_text = data.get('text') or data.get('transcription') or data.get('content')

        if not transcription_text:
            return jsonify({'error': 'No transcription text found in request. Expected "text", "transcription", or "content" field'}), 400

        logger.info(f'Received transcription: {transcription_text[:100]}...')

        # Generate filename with timestamp
        now = datetime.now()
        filename = f"transcriptions/{uid}/{now.strftime('%Y/%m/%d')}/{now.strftime('%H_%M_%S')}.txt"

        # Prepare content with metadata
        content = f"""Transcription Time: {now.isoformat()}
User ID: {uid}
Source: Omi Wearable Device

--- TRANSCRIPTION ---
{transcription_text}

--- METADATA ---
{json.dumps(data, indent=2)}
"""

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        logger.info(f'Created temporary transcription file: {temp_path}')

        # Upload to GCS
        try:
            client = get_gcs_client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(filename)

            # Upload file with content type
            blob.upload_from_filename(temp_path, content_type='text/plain')

            logger.info(f'Successfully uploaded {filename} to GCS bucket {bucket_name}')
            success = True

        except Exception as e:
            logger.error(f'Failed to upload transcription to GCS: {e}')
            success = False

        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except Exception as e:
            logger.warning(f'Failed to delete temporary file: {e}')

        if success:
            return jsonify({
                'success': True,
                'message': 'Transcription received and stored successfully',
                'filename': filename,
                'uid': uid,
                'length': len(transcription_text)
            }), 200
        else:
            return jsonify({
                'error': 'Failed to upload to Google Cloud Storage'
            }), 500

    except Exception as e:
        logger.error(f'Error processing transcription: {e}')
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'omi-audio-streaming-server',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET', 'POST'])
def root():
    """Root endpoint - handles both GET for info and POST for audio (compatibility)."""
    if request.method == 'POST':
        # If POST request to root, redirect to audio handler
        logger.info('POST request received at root /, processing as audio webhook')
        return handle_audio()

    # GET request - return service information
    return jsonify({
        'name': 'Omi Audio Streaming Server',
        'version': '1.0.0',
        'description': 'Receives audio bytes and transcriptions from Omi wearable devices and saves to GCS',
        'endpoints': {
            '/audio': 'POST - Receive and process audio bytes',
            '/transcription': 'POST - Receive and store transcription text',
            '/': 'POST - Also accepts audio bytes (compatibility)',
            '/health': 'GET - Health check'
        },
        'documentation': 'https://docs.omi.me/doc/developer/AudioStreaming'
    }), 200


if __name__ == '__main__':
    # Validate environment variables on startup
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        logger.warning('GOOGLE_APPLICATION_CREDENTIALS_JSON not set - GCS uploads will fail')

    if not os.getenv('GCS_BUCKET_NAME'):
        logger.warning('GCS_BUCKET_NAME not set - GCS uploads will fail')

    # Run Flask app
    port = int(os.getenv('PORT', 8080))
    logger.info(f'Starting server on port {port}...')
    app.run(host='0.0.0.0', port=port, debug=False)
