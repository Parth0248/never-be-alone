# Omi Transcription Webhook Setup

This guide explains how to configure your Omi wearable device to send transcriptions to your Cloud Run endpoint.

## Cloud Run Endpoint

Your transcription endpoint is now live at:

```
https://omi-audio-server-423984362325.us-central1.run.app/transcription
```

## Available Endpoints

The server provides the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/audio` | POST | Receive raw audio bytes from Omi device |
| `/transcription` | POST | Receive and store transcription text |
| `/health` | GET | Health check endpoint |
| `/` | GET | Service information |

## Setting up Transcription Webhook in Omi App

### Step 1: Open Omi Mobile App
1. Open the Omi app on your phone
2. Go to Settings or Device Configuration

### Step 2: Configure Webhook URL
1. Find the "Transcription Webhook" or "Memory Webhook" setting
2. Enter the following URL:
   ```
   https://omi-audio-server-423984362325.us-central1.run.app/transcription?uid=YOUR_USER_ID
   ```
3. Replace `YOUR_USER_ID` with your unique identifier (e.g., your email or user ID)

### Step 3: Test the Connection
Send a test transcription from the Omi app to verify the setup.

## Transcription Data Format

The endpoint expects JSON data with the following fields:

```json
{
  "text": "The transcribed audio content",
  "timestamp": "2025-10-25T10:30:00Z",
  "duration": 5.2,
  "language": "en"
}
```

**Required fields:**
- `text`, `transcription`, or `content` - The transcribed text (at least one must be present)

**Optional fields:**
- `timestamp` - ISO 8601 timestamp
- `duration` - Audio duration in seconds
- `language` - Language code
- Any other metadata you want to include

## How Transcriptions are Stored

Transcriptions are stored in Google Cloud Storage with the following structure:

```
transcriptions/
  └── {user_id}/
      └── {year}/
          └── {month}/
              └── {day}/
                  └── {hour}_{minute}_{second}.txt
```

Example:
```
transcriptions/test_user_123/2025/10/25/19_22_59.txt
```

Each file contains:
- Transcription timestamp
- User ID
- Source information
- The transcription text
- Full metadata in JSON format

## Testing Your Setup

Use the provided test script to verify your endpoint:

```bash
python test_transcription_endpoint.py
```

Expected response:
```json
{
  "success": true,
  "message": "Transcription received and stored successfully",
  "filename": "transcriptions/test_user_123/2025/10/25/19_22_59.txt",
  "uid": "test_user_123",
  "length": 81
}
```

## Viewing Your Transcriptions

### Method 1: Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to Cloud Storage
3. Open your bucket: `omi-audio-files`
4. Browse to `transcriptions/{your_uid}/`

### Method 2: Using gsutil CLI
```bash
# List all transcriptions for a user
gsutil ls gs://omi-audio-files/transcriptions/YOUR_USER_ID/

# Download a specific transcription
gsutil cp gs://omi-audio-files/transcriptions/YOUR_USER_ID/2025/10/25/*.txt .

# View the content directly
gsutil cat gs://omi-audio-files/transcriptions/YOUR_USER_ID/2025/10/25/19_22_59.txt
```

## Troubleshooting

### Webhook Not Receiving Data
1. Check that the URL is correct and includes the `?uid=YOUR_USER_ID` parameter
2. Verify your Omi device has internet connectivity
3. Check the Cloud Run logs:
   ```bash
   gcloud run services logs read omi-audio-server --region us-central1 --limit 50
   ```

### Permission Errors
Ensure your GCP service account has the following permissions:
- `storage.objects.create`
- `storage.objects.get`
- `storage.buckets.get`

### Data Format Issues
The endpoint accepts flexible field names for the transcription text:
- `text`
- `transcription`
- `content`

If none of these fields are present, you'll receive an error. Check your Omi app's transcription format.

## Next Steps

1. Test the endpoint with real Omi device transcriptions
2. Set up notifications or alerts for new transcriptions
3. Integrate with Supermemory for advanced memory features
4. Build custom analysis tools on top of stored transcriptions

## Support

For issues or questions:
- Check Cloud Run logs: `gcloud run services logs read omi-audio-server --region us-central1`
- Review the main README: [README.md](README.md)
- Omi Documentation: https://docs.omi.me
