# Reka.AI Integration with OMI Glasses - Complete Guide

## 🎯 Overview

This integration connects your OMI glasses with Reka.AI's multimodal AI to provide intelligent, context-aware responses based on what you see and hear.

### How It Works

1. **OMI Glasses** capture images and audio from your environment
2. **Webhooks** send this data to your server
3. **Reka.AI** processes the multimodal data (images + audio + context)
4. **Supermemory** provides relevant historical context
5. **Response** is sent back to your OMI app

## 📋 Components

### Core Files

- `reka_client.py` - Reka.AI API client for multimodal processing
- `omi_client.py` - OMI App API client for sending responses
- `webhook_server.py` - Flask server to receive OMI webhooks
- `test_reka_integration.py` - Test suite for the complete pipeline

### Configuration

- `.env` - API keys and configuration
- `requirements.txt` - Python dependencies

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:

```bash
# Reka.AI API
REKA_API_KEY=23ef06698f0d9ae403ac545ab50618560a9c36343c28adbcab6cbd4eef377136
REKA_MODEL=reka-flash

# OMI App API
OMI_API_KEY=sk_bebf536cfcd4070025815eaf32e767a1
OMI_APP_ID=01K8FEGG4NNEN1Q8384FQT4DM9
OMI_USER_ID=your_omi_user_id_here  # Get this from your OMI app

# Supermemory API
SUPERMEMORY_API_KEY=sm_ABpjkMjHLz4JMAfthSbBph_msXeoCXCOSLKUbvCchQPZFlHrRIezInSzzCTEdSZtEzWgrgJlqmdKmgFvGDzgWLO

# Server
PORT=3000
```

**Important:** You need to get your `OMI_USER_ID` from the OMI app to send responses back.

### 3. Run Tests

Test the integration before starting the server:

```bash
python test_reka_integration.py
```

This will run 3 tests:
1. Simple text query to Reka.AI
2. Image + text query with sample data
3. Full pipeline with webhook data

### 4. Start the Webhook Server

```bash
python webhook_server.py
```

The server will start on `http://localhost:3000` with these endpoints:

- `POST /webhook/audio` - Receive audio transcripts
- `POST /webhook/images` - Receive images and context
- `POST /webhook/combined` - Receive combined data
- `GET /health` - Health check

## 🔧 Configuration

### OMI Webhook URLs

Configure these webhooks in your OMI app:

- **Audio Transcript Webhook:** `https://webhook.site/7d8f3163-874e-4491-a29e-b0be42902456`
- **Images/Context Webhook:** `https://webhook.site/4cbaf51e-538f-4bd9-9a0b-96da59c50a62`

**Note:** These are currently pointing to webhook.site for testing. For production:

1. Deploy your webhook server (e.g., using Railway, Heroku, or Google Cloud Run)
2. Update the webhook URLs in OMI app settings to point to your server:
   - Audio: `https://your-domain.com/webhook/audio`
   - Images: `https://your-domain.com/webhook/images`

### Reka.AI Models

You can change the model in `.env`:

- `reka-flash` - Fast, efficient model (default)
- `reka-core` - More capable, balanced model
- `reka-edge` - Lightweight model for quick responses

## 📚 API Usage

### Reka Client

```python
from reka_client import RekaClient

client = RekaClient()

# Simple text query
result = client.simple_query("What is machine learning?")
print(result['response'])

# Query with images
result = client.simple_query(
    "What do you see in these images?",
    images_base64=["base64_encoded_image_1", "base64_encoded_image_2"]
)

# Process OMI data (used by webhook server)
result = client.process_omi_data(
    images_base64=["img1", "img2"],
    audio_transcript="User said: How do I solve this problem?",
    context_overview="User is at a coding session",
    supermemory_context="Relevant past context..."
)
```

### OMI Client

```python
from omi_client import OmiClient

client = OmiClient()

# Send a notification
result = client.send_notification("Hello from your AI assistant!")

# Send an AI response
result = client.send_response(
    response_text="Here's how to solve that problem...",
    original_context="User asked about async programming"
)

# Create a conversation
result = client.create_conversation(
    text="Full conversation text here",
    text_source="other_text",
    text_source_spec="ai_assistant"
)

# Create memories
result = client.create_memories(
    text="Important information to remember...",
    text_source="other",
    text_source_spec="ai_assistant"
)
```

## 🔄 Webhook Data Flow

### Audio Webhook Payload

```json
{
  "text": "User said: What's the weather like?",
  "timestamp": "2025-10-26T12:00:00Z",
  "language": "en"
}
```

### Image Webhook Payload

```json
{
  "photos": [
    {
      "id": "photo-id",
      "base64": "base64_encoded_image_data..."
    }
  ],
  "structured": {
    "title": "Scene Title",
    "overview": "Detailed description of the scene...",
    "category": "technology"
  },
  "created_at": "2025-10-26T12:00:00Z"
}
```

### Processing Logic

The webhook server intelligently combines audio and image data:

1. When audio is received, it checks for recent images (within 60 seconds)
2. When images are received, it checks for recent audio (within 60 seconds)
3. If both are available, it processes them together through Reka.AI
4. The response is sent back to the OMI app

## 🧪 Testing

### Test with Sample Data

The repository includes `webhook.json` with sample OMI data. Run tests:

```bash
# Run all tests
python test_reka_integration.py

# Test individual clients
python reka_client.py
python omi_client.py
```

### Test Webhooks

Use `curl` to test the webhook endpoints:

```bash
# Test audio webhook
curl -X POST http://localhost:3000/webhook/audio \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "timestamp": "2025-10-26T12:00:00Z"}'

# Test image webhook
curl -X POST http://localhost:3000/webhook/images \
  -H "Content-Type: application/json" \
  -d @webhook.json

# Health check
curl http://localhost:3000/health
```

## 🚀 Deployment

### Option 1: Local Development

```bash
python webhook_server.py
```

Use ngrok to expose your local server:

```bash
ngrok http 3000
```

Then update OMI webhook URLs to your ngrok URL.

### Option 2: Cloud Deployment (Recommended)

#### Railway

1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard
4. Deploy!

#### Google Cloud Run

1. Build Docker image:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "webhook_server.py"]
```

2. Deploy:

```bash
gcloud run deploy omi-webhook \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🐛 Troubleshooting

### Common Issues

1. **"OMI_USER_ID not configured"**
   - Get your user ID from the OMI app settings
   - Update `.env` file with your user ID

2. **"Reka API request failed"**
   - Check your API key is correct
   - Verify you have credits/quota remaining
   - Check if base64 images are too large

3. **"Failed to create conversation in OMI"**
   - Verify your OMI_API_KEY and OMI_APP_ID
   - Ensure your app has the correct permissions in OMI
   - Check that the user has enabled your app

4. **Webhook not receiving data**
   - Verify webhook URLs are correct in OMI app
   - Check firewall/network settings
   - Use webhook.site to debug incoming payloads

### Debug Mode

Enable Flask debug mode in `webhook_server.py`:

```python
app.run(host='0.0.0.0', port=port, debug=True)
```

## 📊 Monitoring

Check server logs for:

- Incoming webhook data
- Reka.AI processing results
- OMI app response status
- Error messages

The webhook server logs all operations with timestamps and status indicators.

## 🔐 Security Notes

1. **Never commit `.env` file** to version control
2. Use environment variables in production
3. Consider adding webhook signature verification
4. Use HTTPS in production
5. Rate limit your endpoints

## 📈 Next Steps

1. **Supermemory Integration:** Implement context retrieval from Supermemory
2. **Advanced Prompting:** Customize Reka prompts for your use case
3. **Error Handling:** Add retry logic and better error recovery
4. **Caching:** Cache recent responses to reduce API calls
5. **Analytics:** Track usage and response quality

## 🆘 Support

- Reka.AI Docs: https://docs.reka.ai
- OMI API Docs: https://docs.omi.me
- Issues: Create an issue in your repository

## 📝 License

[Your License Here]

---

Built with ❤️ for the Never Be Alone project
