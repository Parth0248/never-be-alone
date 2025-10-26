# Omi Device Webhook Integration Guide

Complete guide to connect your Omi wearable device to the agent orchestration system.

## Overview

Your Omi device will send live transcriptions → Agent Orchestrator → Process with AI → Execute Actions → Send to webhook.site for monitoring

```
Omi Device (on your body)
    ↓ [sends transcription]
Agent Orchestrator (localhost:8080)
    ↓ [processes with ASI:One + agents]
Actions Executed (reminders, searches, etc.)
    ↓ [monitoring]
Webhook.site (https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9)
```

## Setup Instructions

### Step 1: Test ASI:One API Connection

First, verify the new API key works:

```bash
cd agent-orchestrator
python test_asi_one_api.py
```

Expected output:
```
✅ SUCCESS!
Response:
  Model: asi1-fast-agentic
  Message: [response text]
```

### Step 2: Start the Omi Webhook Server

```bash
cd agent-orchestrator
python omi_webhook_integration.py
```

Server will start on `http://localhost:8080` with these endpoints:

- **POST /omi/transcription** - Receives transcriptions from Omi
- **POST /omi/audio** - Receives raw audio (future use)
- **POST /test** - Test the integration
- **GET /health** - Health check

### Step 3: Test the Integration Locally

Open a new terminal and test:

```bash
curl -X POST http://localhost:8080/test \
  -H "Content-Type: application/json" \
  -d '{"text": "Remind me to buy groceries"}'
```

Check https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9 to see the result!

### Step 4: Configure Omi Device

#### Option A: Using Omi DevKit 2

1. Go to Omi mobile app settings
2. Find "Webhook Configuration" or "Developer Settings"
3. Set webhook URL to your server (see Step 5 for public URL)
4. Select webhook events: "Transcription Complete"

#### Option B: Using Omi Glass

1. Open Omi Glass companion app
2. Navigate to Settings → Developer → Webhooks
3. Add webhook endpoint
4. Enable "Real-time Transcription" events

### Step 5: Expose Local Server (for Omi to reach it)

Since Omi needs to reach your local server, you need a public URL. Use one of these:

#### Option 1: ngrok (Recommended)

```bash
# Install ngrok from https://ngrok.com/download
ngrok http 8080
```

You'll get a URL like: `https://abc123.ngrok.io`

Use this in Omi settings:
- Webhook URL: `https://abc123.ngrok.io/omi/transcription`

#### Option 2: Cloudflare Tunnel

```bash
# Install cloudflared
cloudflared tunnel --url http://localhost:8080
```

#### Option 3: Deploy to Cloud Run (Production)

See `DEPLOYMENT.md` for instructions.

### Step 6: Configure Omi Webhook

In your Omi app/settings, set:

**Webhook URL**: `https://YOUR-NGROK-URL/omi/transcription`

**Headers** (if needed):
```json
{
  "Content-Type": "application/json"
}
```

**Events to send**:
- ✅ Transcription Complete
- ✅ Session Complete (optional)

## Webhook Payload Format

The server expects transcriptions in this format:

### Format 1: Omi Segments (Recommended)

```json
{
  "session_id": "session_12345",
  "segments": [
    {
      "text": "Remind me to call mom tomorrow",
      "speaker": "SPEAKER_00",
      "start": 0.0,
      "end": 3.5,
      "is_user": true
    }
  ]
}
```

### Format 2: Simple Transcription

```json
{
  "transcription": "Remind me to call mom tomorrow",
  "uid": "user_123",
  "timestamp": "2025-10-25T15:30:00Z"
}
```

### Format 3: Direct Text

```json
{
  "text": "Remind me to call mom tomorrow"
}
```

All formats are supported!

## Testing the Full Flow

### Test 1: Local Test

```bash
curl -X POST http://localhost:8080/omi/transcription \
  -H "Content-Type: application/json" \
  -d '{
    "transcription": "Remind me to call John tomorrow at 3pm",
    "uid": "test_user",
    "timestamp": "2025-10-25T15:30:00Z"
  }'
```

### Test 2: Segment Format

```bash
curl -X POST http://localhost:8080/omi/transcription \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "segments": [
      {
        "text": "Schedule a meeting with the team",
        "speaker": "SPEAKER_00",
        "is_user": true
      },
      {
        "text": "tomorrow at 10am",
        "speaker": "SPEAKER_00",
        "is_user": true
      }
    ]
  }'
```

### Test 3: Check webhook.site

Visit: https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9

You should see:
1. **omi_transcription_received** - Original transcription
2. **agent_processing_complete** - Processing results
3. Intent, confidence, actions taken

## What Happens When Omi Sends Transcription

```
1. Omi captures your speech
2. Omi transcribes → sends to your server
3. Server receives transcription
4. Sends to webhook.site (for monitoring)
5. ASI:One analyzes intent
6. Routes to appropriate agent(s):
   - Calendar Agent: Creates reminders
   - Context Agent: Searches memories
   - Task Agent: Analyzes & categorizes
7. Agents execute actions
8. Stores in Supermemory
9. Sends results to webhook.site
10. Returns success to Omi
```

## Monitoring & Debugging

### Real-time Monitoring

Open webhook.site in your browser:
https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9

You'll see all events in real-time:
- Transcriptions received
- Agent processing results
- Errors (if any)

### Server Logs

Watch the server logs:
```bash
# Server shows detailed logs
2025-10-25 15:30:00 - INFO - Received Omi transcription: ...
2025-10-25 15:30:01 - INFO - Intent detected: create_reminder
2025-10-25 15:30:02 - INFO - calendar_agent completed: Reminder created
```

### Check Agent Status

```bash
curl http://localhost:8080/health
```

## Troubleshooting

### Problem: Omi not sending webhooks

**Check:**
1. Is ngrok/tunnel running?
2. Is webhook URL correct in Omi settings?
3. Is Omi connected to internet?
4. Check Omi app logs

**Solution:**
```bash
# Restart ngrok
ngrok http 8080

# Update Omi settings with new URL
```

### Problem: Transcriptions received but not processed

**Check:**
```bash
curl http://localhost:8080/health
```

**Solution:**
```bash
# Restart server
python omi_webhook_integration.py
```

### Problem: ASI:One timing out

**Solution:** The fallback system handles this automatically. Check logs to see if fallback is being used.

### Problem: No data on webhook.site

**Check:**
1. Is URL correct? https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9
2. Is server running?
3. Are transcriptions being received?

## Example: Complete Flow

### You say to Omi:
> "Remind me to call Sarah tomorrow at 2pm"

### Server receives:
```json
{
  "segments": [
    {"text": "Remind me to call Sarah tomorrow at 2pm"}
  ]
}
```

### webhook.site shows:
```json
{
  "event": "omi_transcription_received",
  "transcription": "Remind me to call Sarah tomorrow at 2pm",
  "timestamp": "2025-10-25T15:30:00Z"
}
```

### Agent processes:
- Intent: `create_reminder` (confidence: 0.85)
- Entities: action=call, person=Sarah, time=tomorrow at 2pm
- Agent: calendar_agent
- Action: create_reminder

### webhook.site shows result:
```json
{
  "event": "agent_processing_complete",
  "result": {
    "intent": "create_reminder",
    "confidence": 0.85,
    "actions_taken": [
      "calendar_agent: Reminder created for 2025-10-26 14:00:00"
    ]
  }
}
```

### Result:
✅ Reminder created!
✅ Stored in Supermemory
✅ Visible on webhook.site

## Production Deployment

For production use, deploy to Cloud Run or similar:

```bash
# See DEPLOYMENT.md for full instructions
gcloud run deploy omi-agent-orchestrator \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

Then update Omi with the Cloud Run URL.

## Security Considerations

### For Production

1. **Add Authentication**
   - Add API key verification
   - Verify Omi signature

2. **Rate Limiting**
   - Limit requests per user
   - Prevent abuse

3. **HTTPS Only**
   - Always use HTTPS in production
   - ngrok provides HTTPS automatically

### Example: Add API Key

```python
@app.route('/omi/transcription', methods=['POST'])
def receive_omi_transcription():
    # Verify API key
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('OMI_API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401

    # Process transcription...
```

## Next Steps

1. ✅ Start server: `python omi_webhook_integration.py`
2. ✅ Expose with ngrok: `ngrok http 8080`
3. ✅ Configure Omi with ngrok URL
4. ✅ Test: Say something to your Omi device
5. ✅ Check webhook.site for results!

## Support

- Server logs: Check terminal output
- webhook.site: https://webhook.site/8d1347f7-8dfd-4d6f-803d-bd08f9a571c9
- Test endpoint: `POST /test`
- Health check: `GET /health`

---

**You're all set! Start speaking to your Omi device and watch the AI agents process your requests in real-time!** 🎙️🤖
