# Snap Spectacles + Omi Multimodal Integration

## System Status: READY

Your multimodal pipeline is complete and ready for Snap Spectacles integration!

## Architecture Overview

```
┌─────────────────┐         ┌──────────────┐
│ Snap Spectacles │────────>│    Video     │
│   (Video Feed)  │         │              │
└─────────────────┘         │              │
                            │   Reka.ai    │
┌─────────────────┐         │  (Multimodal │
│   Omi Device    │────────>│  Processing) │
│  (Audio Feed)   │         │              │
└─────────────────┘         └──────┬───────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Decision Logic    │
                        │  Simple Q&A vs      │
                        │  Agent Workflow?    │
                        └──────┬──────┬───────┘
                               │      │
                    ┌──────────▼      ▼──────────┐
                    │                             │
            ┌───────▼────────┐        ┌──────────▼────────┐
            │  Direct Answer │        │  ASI:One Routing  │
            │   (Fast)       │        │  (Agent Workflow) │
            └────────────────┘        └───────┬───────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │   Supermemory     │
                                    │   (Permanent)     │
                                    └───────────────────┘
```

## Components Implemented

### 1. Spectacles Webhook Server (`spectacles_webhook.py`)
**Status**: ✅ Complete

**Endpoint**: `POST /api/spectacles/video`

**Accepts**:
- `video` (file): Video from Snap Spectacles
- `question` (optional): What to analyze (default: "What is happening in this video?")
- `audio_context` (optional): Related Omi transcript for context

**Flow**:
1. Upload video to Reka.ai
2. Process video Q&A with audio context
3. Decision routing:
   - **Simple queries** → Reka answers directly
   - **Action requests** → Routes to ASI:One agents

**Keywords that trigger agent routing**:
- "remind me", "schedule", "create", "send", "book"
- "order", "buy", "set reminder", "add to calendar"
- "email", "message", "call", "search for"

### 2. Reka Client (`reka_client.py`)
**Status**: ✅ Complete

**Video Capabilities**:
- `upload_video()`: Upload video files to Reka
- `video_qa()`: Ask questions about videos with optional audio context
- Streaming support for real-time responses

### 3. Omi Webhook Poller (`webhook_poller.py`)
**Status**: ✅ Running

Polls webhook.site every 5 seconds for Omi transcriptions and processes through:
1. Reka.ai context enhancement
2. ASI:One intent analysis
3. Agent execution
4. Supermemory storage

## How to Start Spectacles Server

```bash
cd agent-orchestrator
python spectacles_webhook.py
```

This starts the server on `http://0.0.0.0:5000`

## Testing the Spectacles Integration

### Test Script
Use the included test script `test_spectacles_webhook.py`:

```bash
python test_spectacles_webhook.py
```

### Manual Testing with cURL

#### Simple Video Question (Direct Answer)
```bash
curl -X POST http://localhost:5000/api/spectacles/video \
  -F "video=@test_video.mp4" \
  -F "question=What color is the object?"
```

#### Video + Audio Context
```bash
curl -X POST http://localhost:5000/api/spectacles/video \
  -F "video=@test_video.mp4" \
  -F "question=What am I looking at?" \
  -F "audio_context=I just mentioned this is my favorite coffee shop"
```

#### Action Request (Routes to Agents)
```bash
curl -X POST http://localhost:5000/api/spectacles/video \
  -F "video=@test_video.mp4" \
  -F "question=Remind me to come back here next week"
```

### Expected Response Formats

**Direct Answer (Simple Query)**:
```json
{
  "success": true,
  "type": "direct_answer",
  "answer": "I see a red coffee mug on a wooden table.",
  "video_id": "reka_video_id_here",
  "reka_confidence": 0.9
}
```

**Agent Workflow (Complex Task)**:
```json
{
  "success": true,
  "type": "agent_workflow",
  "reka_understanding": "User wants to set a reminder about this location.",
  "video_id": "reka_video_id_here",
  "agent_result": {
    "intent": "create_reminder",
    "actions_taken": ["calendar_agent: Created reminder for next week"],
    "results": [...]
  }
}
```

## Integration Points for Snap Spectacles

### Option 1: Direct HTTP POST
Configure Spectacles to POST video directly to:
```
POST http://your-server:5000/api/spectacles/video
```

### Option 2: Combined with Omi
1. Omi device captures audio → Webhook → Orchestrator
2. Spectacles captures video → Same orchestrator
3. Both contexts merged in Reka.ai

### Option 3: Synchronized Feed
Time-synchronized audio + video:
```python
# In your Spectacles app
video_frame = capture_video()
recent_audio = get_recent_omi_transcript()

requests.post(
    "http://your-server:5000/api/spectacles/video",
    files={"video": video_frame},
    data={
        "question": "What should I do here?",
        "audio_context": recent_audio
    }
)
```

## Current System Status

### ✅ Working
- Omi webhook poller (running in background)
- Supermemory storage via MCP
- ASI:One intent detection
- Agent orchestration
- Spectacles webhook server (code ready)

### ⚠️ Needs Testing
- Reka video upload (waiting for real video)
- Reka video Q&A with streaming
- Decision logic with real queries
- Spectacles hardware integration

### 🔧 Recent Fix
- Changed Reka API format from `"text"` to `"content"` field

## Environment Variables Required

All already configured in `.env`:
```
REKA_API_KEY=23ef06698f0d9ae403ac545ab50618560a9c36343c28adbcab6cbd4eef377136
REKA_MODEL=reka-flash
ASI_ONE_API_KEY=sk_7f1753d0aa3448139f4a3a995f5eb1d86c2db33367ec41d7a5f9581b43492670
SUPERMEMORY_API_KEY=sm_ABpjkMjHLz4JMAfthSbBph_msXeoCXCOSLKUbvCchQPZFlHrRIezInSzzCTEdSZtEzWgrgJlqmdKmgFvGDzgWLO
```

## Next Steps

1. **When Spectacles are integrated**: Start the webhook server
   ```bash
   python spectacles_webhook.py
   ```

2. **Configure Spectacles**: Point video feed to `POST /api/spectacles/video`

3. **Test with sample video**: Use the test script to verify the pipeline

4. **Monitor logs**: Watch console output for:
   - Video upload success
   - Reka Q&A results
   - Decision routing (direct vs agents)
   - Supermemory storage

## Support

The system includes detailed emoji logging at every step:
- 📹 Video operations
- 🤖 Reka.ai processing
- 🎤 Audio context
- 🗺️ Agent routing
- 💾 Supermemory storage
- ✅ Success indicators
- ❌ Error indicators

All ready for your Spectacles integration! 🎉
