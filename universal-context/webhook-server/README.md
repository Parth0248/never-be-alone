# Omi Audio Streaming Server

A Python-based webhook server that receives raw audio bytes from Omi wearable devices and saves them as WAV files in Google Cloud Storage.

## Features

- **Audio Streaming**: Receives raw audio bytes (PCM format) from Omi devices
- **WAV Conversion**: Converts raw PCM audio to WAV format with proper headers
- **GCS Storage**: Automatically uploads audio files to Google Cloud Storage
- **Simple Architecture**: Direct webhook-to-storage pipeline without intermediary services
- **Docker Support**: Easy deployment with Docker container
- **Health Monitoring**: Built-in health check endpoint

## Architecture

```
Omi Device (DevKit 2 / Glass)
    |
    v
Audio Webhook (/audio)
    |
    ├─> Receive raw PCM audio bytes
    ├─> Add WAV header (44 bytes)
    ├─> Create timestamped filename
    └─> Upload to Google Cloud Storage
```

## Prerequisites

- Python 3.12+
- Google Cloud Platform account with billing enabled
- GCS bucket created
- Service account with Storage Object Admin permissions
- Omi wearable device (DevKit 2 or Glass)

## Audio Format Details

### Omi DevKit 2 Specifications
- **Format**: Raw PCM (16-bit little-endian)
- **Sample Rate**: 16,000 Hz
- **Channels**: 1 (mono)
- **Bits Per Sample**: 16

### WAV Conversion
Raw PCM audio is converted to WAV format with a 44-byte header containing:
- RIFF chunk descriptor
- Format chunk (PCM audio format)
- Data chunk with audio samples

## Setup

### 1. GCP Setup (Completed)

The following GCP resources have been set up:

- **Project**: `calhacks-omi-audio`
- **Service Account**: `omi-audio-server@calhacks-omi-audio.iam.gserviceaccount.com`
- **GCS Bucket**: `calhacks-omi-audio-files` (us-central1)
- **Credentials**: Saved in `gcp-credentials.json` (already base64 encoded in `.dev.vars`)

### 2. Install Python Dependencies

**IMPORTANT**: Always use the virtual environment before installing packages.

On Windows PowerShell:
```powershell
cd universal-context\webhook-server

# Create virtual environment (first time only)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

The `.dev.vars` file has been created with your GCP credentials:

```env
GOOGLE_APPLICATION_CREDENTIALS_JSON=<base64_encoded_credentials>
GCS_BUCKET_NAME=calhacks-omi-audio-files
PORT=8080
```

For other environments, copy `.env.example` and fill in your credentials:
```bash
cp .env.example .env
```

## Development

### Run Locally

Make sure your virtual environment is activated:

```powershell
# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Run the server
python main.py
```

The server will start at `http://localhost:8080`

### Test Endpoints

#### Health Check
```bash
curl http://localhost:8080/health
```

#### Test Audio Upload
```bash
# Create a test audio file or use webhook.site for testing
curl -X POST "http://localhost:8080/audio?uid=test_user&sample_rate=16000" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @test_audio.raw
```

## Deployment

### Option 1: Local Deployment with Ngrok

For testing with the Omi app without deploying to cloud:

```bash
# Install ngrok (if not already installed)
# Download from https://ngrok.com/download

# Run your server
python main.py

# In another terminal, expose it
ngrok http 8080
```

Use the ngrok URL (e.g., `https://abc123.ngrok.io/audio`) in your Omi app settings.

### Option 2: Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker build -t omi-audio-server .

# Run the container
docker run -p 8080:8080 \
  -e GOOGLE_APPLICATION_CREDENTIALS_JSON="<your_base64_encoded_credentials>" \
  -e GCS_BUCKET_NAME="calhacks-omi-audio-files" \
  omi-audio-server
```

### Option 3: Deploy to GCP Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/calhacks-omi-audio/omi-audio-server

# Deploy to Cloud Run
gcloud run deploy omi-audio-server \
  --image gcr.io/calhacks-omi-audio/omi-audio-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS_JSON="<base64_credentials>",GCS_BUCKET_NAME="calhacks-omi-audio-files"
```

### Option 4: Deploy to Other Cloud Providers

The Docker container can be deployed to:
- AWS (ECS, EC2, App Runner)
- DigitalOcean (App Platform, Droplets)
- Azure (Container Instances, App Service)
- Heroku

## Configure Omi Device

Once your server is deployed and accessible via a public URL:

1. Open the Omi app on your phone
2. Go to **Settings** > **Developer Mode**
3. Under **Realtime audio bytes**, configure:
   - **Endpoint**: `https://your-server-url/audio?uid=YOUR_USER_ID`
   - **Every x seconds**: 5 (or your preferred interval)

Example endpoints:
- Local with ngrok: `https://abc123.ngrok.io/audio?uid=user123`
- Cloud Run: `https://omi-audio-server-xyz.run.app/audio?uid=user123`
- Webhook.site: `https://webhook.site/unique-url` (for testing)

## API Reference

### POST /audio

Receives raw audio bytes from Omi device and uploads to GCS.

**Query Parameters:**
- `uid` (required): User identifier
- `sample_rate` (optional): Audio sample rate in Hz (default: 16000)

**Request Body:** Raw audio bytes (application/octet-stream)

**Response:**
```json
{
  "success": true,
  "message": "Audio bytes received and uploaded as 25_10_2025_14_30_45.wav",
  "filename": "25_10_2025_14_30_45.wav",
  "uid": "user123",
  "size_bytes": 160000
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "omi-audio-streaming-server",
  "timestamp": "2025-10-25T14:30:45.123Z"
}
```

### GET /

Service information endpoint.

**Response:**
```json
{
  "name": "Omi Audio Streaming Server",
  "version": "1.0.0",
  "description": "Receives audio bytes from Omi wearable devices and saves as WAV files in GCS",
  "endpoints": {
    "/audio": "POST - Receive and process audio bytes",
    "/health": "GET - Health check"
  },
  "documentation": "https://docs.omi.me/doc/developer/AudioStreaming"
}
```

## Project Structure

```
webhook-server/
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container configuration
├── .env.example           # Environment variables template
├── .dev.vars              # Local environment variables (gitignored)
├── .gitignore             # Git ignore rules
├── gcp-credentials.json   # GCS service account key (gitignored)
├── TASK_LOG.txt           # Project task tracking log
├── omi-audio-streaming/   # Reference Go implementation
└── README.md              # This file
```

## File Naming Convention

Audio files are saved with timestamps in the format:
```
DD_MM_YYYY_HH_MM_SS.wav
```

Example: `25_10_2025_14_30_45.wav`

## Viewing Uploaded Files

To view files in your GCS bucket:

```bash
# List all files
gcloud storage ls gs://calhacks-omi-audio-files/

# Download a specific file
gcloud storage cp gs://calhacks-omi-audio-files/25_10_2025_14_30_45.wav .

# View in Google Cloud Console
# https://console.cloud.google.com/storage/browser/calhacks-omi-audio-files
```

## Testing with Webhook.site

For initial testing without running the server:

1. Go to https://webhook.site/
2. Copy your unique URL
3. Configure in Omi app: `https://webhook.site/your-unique-id`
4. Audio bytes will be displayed in webhook.site dashboard

## Troubleshooting

### Virtual Environment Issues
```powershell
# If activation fails, enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\.venv\Scripts\Activate.ps1
```

### GCS Upload Errors
- Verify credentials are correctly base64 encoded
- Check service account has `roles/storage.objectAdmin` permission
- Ensure bucket name is correct
- Verify billing is enabled on GCP project

### Audio Format Issues
- Verify Omi device is sending PCM 16-bit audio
- Check sample rate matches (16000 Hz for DevKit 2)
- Ensure Content-Type is `application/octet-stream`

### Port Already in Use
```bash
# Change port in .dev.vars or use environment variable
PORT=8081 python main.py
```

## Development Notes

- Always activate `.venv` before installing packages
- Keep `TASK_LOG.txt` updated with progress
- Never commit `gcp-credentials.json` or `.dev.vars`
- Use webhook.site for initial webhook testing

## References

- [Omi Audio Streaming Documentation](https://docs.omi.me/doc/developer/AudioStreaming)
- [Reference Implementation (Go)](https://github.com/mdmohsin7/omi-audio-streaming)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: https://github.com/Parth0248/never-be-alone/issues
- Cal Hacks Discord: #never-be-alone

## Acknowledgments

- **Omi**: For open-source wearable AI devices and documentation
- **Cal Hacks 2025**: Where this project was built
