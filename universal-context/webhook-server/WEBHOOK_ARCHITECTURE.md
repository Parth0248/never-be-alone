# Webhook Architecture - Omi Audio Streaming

## Overview

This document explains how webhooks work in the Omi audio streaming system and how we're using them.

## What is a Webhook?

A **webhook** is simply a URL endpoint that receives data via HTTP POST requests. Think of it as a "callback URL" that external services (like the Omi device) can send data to.

## Our Architecture

### Simplified Flow (Current Implementation)

```
┌─────────────┐
│ Omi Device  │
│ (DevKit 2)  │
└──────┬──────┘
       │ Every X seconds
       │ Raw audio bytes (PCM)
       │ POST request
       ▼
┌─────────────────────────────┐
│  Your Server (Flask)        │
│  Endpoint: /audio           │
│                             │
│  1. Receive audio bytes     │
│  2. Add WAV header          │
│  3. Create timestamped file │
└──────┬──────────────────────┘
       │ Upload
       ▼
┌─────────────────────────────┐
│  Google Cloud Storage       │
│  Bucket: calhacks-omi-...   │
│                             │
│  Files: DD_MM_YYYY_HH_MM... │
└─────────────────────────────┘
```

### Key Points

1. **No Intermediate Storage**: We removed the Cloudflare KV layer for simplicity
2. **Direct Upload**: Audio goes straight from server to GCS
3. **Permanent Storage**: All files stored permanently in GCS bucket
4. **Simple Pipeline**: Omi → Server → GCS (3 hops only)

## How Webhooks Are "Stored"

**Short Answer**: We don't store webhooks - we store the audio data.

**Detailed Explanation**:
- The **webhook URL** is just your server endpoint: `https://your-domain.com/audio`
- You configure this URL once in the Omi app
- The Omi device then repeatedly sends POST requests to this URL
- Each request contains raw audio bytes
- Your server processes and uploads to GCS immediately

## Webhook URL Configuration

### Development (Using webhook.site)

For testing without running your server:

1. Go to https://webhook.site/
2. Get your unique URL: `https://webhook.site/abc-123-def`
3. Add in Omi app: Developer Settings → Realtime audio bytes → Endpoint
4. View incoming requests in webhook.site dashboard

**Note**: webhook.site only displays the data, doesn't process it. Use this for initial testing to see what the Omi device sends.

### Development (Local with Ngrok)

For testing your actual server locally:

```bash
# Terminal 1: Run your server
python main.py

# Terminal 2: Expose it publicly
ngrok http 8080
```

Use the ngrok URL in Omi app:
```
https://abc123.ngrok.io/audio?uid=yourname
```

### Production Deployment

Deploy your server to a cloud provider and use that URL:

**Cloud Run**:
```
https://omi-audio-server-xyz.a.run.app/audio?uid=yourname
```

**DigitalOcean**:
```
https://omi-audio.your-domain.com/audio?uid=yourname
```

## Data Flow Details

### 1. Omi Device Sends Data

**Request**:
```http
POST /audio?uid=user123&sample_rate=16000 HTTP/1.1
Host: your-server.com
Content-Type: application/octet-stream
Content-Length: 160000

[Raw PCM audio bytes]
```

### 2. Server Processes

**Python Code Flow**:
```python
# main.py handle_audio() function

1. Extract uid and sample_rate from query params
2. Read raw audio bytes from request body
3. Create WAV header (44 bytes)
4. Generate timestamp filename: 25_10_2025_14_30_45.wav
5. Write to temporary file (header + audio data)
6. Upload to GCS bucket
7. Delete temporary file
8. Return success response
```

### 3. GCS Storage

**File Structure**:
```
gs://calhacks-omi-audio-files/
├── 25_10_2025_14_30_00.wav  (5 seconds of audio)
├── 25_10_2025_14_30_05.wav  (next 5 seconds)
├── 25_10_2025_14_30_10.wav  (next 5 seconds)
└── ...
```

## Comparison with Previous Architecture

### Previous (Cloudflare Workers + KV + Groq + Supermemory)

```
Omi → Cloudflare Worker → KV Storage (temp) → Groq (transcribe) → Supermemory (permanent)
```

**Complexity**: 5 layers
**Purpose**: Transcribe audio and store text in Supermemory
**Cost**: Multiple services
**Latency**: 2-3 seconds per request

### Current (Python + GCS)

```
Omi → Flask Server → GCS Storage
```

**Complexity**: 3 layers
**Purpose**: Store raw audio files for later processing
**Cost**: GCS storage only
**Latency**: < 500ms per request

## Why This Approach?

### Advantages
1. **Simpler**: Fewer moving parts, easier to debug
2. **Cheaper**: Only pay for GCS storage
3. **Flexible**: Process audio files later however you want
4. **Reliable**: Direct upload, no intermediate caching
5. **Scalable**: GCS handles any volume

### Future Extensions

You can later add:
- **Transcription**: Process GCS files with Whisper API
- **Analysis**: Run ML models on stored audio
- **Search**: Index transcriptions in database
- **Sharing**: Generate signed URLs for audio playback
- **Batch Processing**: Process multiple files together

## Environment Variables

The server needs these environment variables to work:

```bash
# GCP Service Account Credentials (base64 encoded JSON)
GOOGLE_APPLICATION_CREDENTIALS_JSON=ewogICJ0eXBlIjog...

# GCS Bucket Name
GCS_BUCKET_NAME=calhacks-omi-audio-files

# Server Port (optional)
PORT=8080
```

These are loaded from `.dev.vars` file using python-dotenv.

## Testing the Webhook

### 1. Test with curl (Local)

```bash
# Create sample audio file (1 second of silence)
python -c "import struct; data = struct.pack('<h', 0) * 16000; open('test.raw', 'wb').write(data)"

# Send to your server
curl -X POST "http://localhost:8080/audio?uid=test&sample_rate=16000" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @test.raw
```

### 2. Test with webhook.site

1. Go to https://webhook.site/
2. Copy your unique URL
3. Configure in Omi app
4. Speak into your Omi device
5. See raw bytes appear in webhook.site

### 3. Test with Omi device

1. Deploy your server (ngrok/cloud)
2. Configure URL in Omi app: Settings → Developer Mode → Realtime audio bytes
3. Set endpoint: `https://your-url/audio?uid=yourname`
4. Set interval: 5 seconds
5. Tap "Save"
6. Audio should start uploading to GCS

## Viewing Stored Files

### Using gcloud CLI

```bash
# List all files
gcloud storage ls gs://calhacks-omi-audio-files/

# Download a file
gcloud storage cp gs://calhacks-omi-audio-files/25_10_2025_14_30_45.wav .

# Play the file
# (Use any audio player that supports WAV)
```

### Using GCP Console

Visit: https://console.cloud.google.com/storage/browser/calhacks-omi-audio-files

## Troubleshooting

### "Webhook not receiving data"
- Check Omi app has correct URL
- Verify server is running and accessible
- Test with curl first
- Check Omi app logs for errors

### "Files not appearing in GCS"
- Verify `.dev.vars` has correct credentials
- Check service account has Storage Object Admin role
- Test GCS connection: `gcloud storage ls gs://your-bucket/`
- Check server logs for upload errors

### "Audio files are corrupted"
- Verify WAV header is correct (44 bytes)
- Check sample rate matches (16000 Hz)
- Ensure bytes are written in correct order (header first, then data)

## Next Steps

After audio files are stored in GCS:

1. **Transcription**: Use Whisper API to transcribe
2. **Storage**: Store transcriptions in Supermemory
3. **Processing**: Add real-time or batch processing
4. **UI**: Build dashboard to view/search audio
5. **Integration**: Connect to your app's features

## Summary

- **Webhook = URL endpoint** that receives POST requests
- **We don't "store" webhooks** - we store the audio data they send
- **Simple architecture**: Omi → Server → GCS
- **Configure once** in Omi app, receives data continuously
- **All audio permanently stored** in Google Cloud Storage
