# How to View Logs and Transcriptions

## 📊 **Option 1: View Real-Time Logs (Recommended)**

### See logs as audio comes in:

```bash
cd D:\Projects\never-be-alone\universal-context\webhook-server
wrangler tail --format pretty
```

**What you'll see:**
```
POST /webhook/audio - Ok @ 10/25/2025, 2:30:15 AM
  Received 32768 bytes of audio from user IobOxgj7...
  Converted audio to WAV format (33000 bytes)
  Transcription completed: "Hello, how are you today?"
  Stored transcription in Supermemory with ID: abc123
```

**I'm already running this for you in the background!**

---

## 💾 **Option 2: View Transcriptions in Supermemory**

### Python Script (Simple):

```bash
cd D:\Projects\never-be-alone
python view_transcriptions_simple.py
```

This will show all transcriptions stored in Supermemory.

### Python Script (Detailed):
```python
from supermemory import Supermemory

client = Supermemory(
    api_key="your_key_here",
    base_url="https://api.supermemory.ai/"
)

# Search for transcriptions
results = client.search.execute(q="your search query")

for result in results.results:
    print(result)
```

---

## 🌐 **Option 3: View Logs in Cloudflare Dashboard**

1. Open: https://dash.cloudflare.com/c6d4781a8cc477cef984a8aa83bec2da/workers
2. Click on "never-be-alone-webhook-server"
3. Go to "Logs" tab
4. See real-time logs with filtering options

---

## 📦 **Option 4: Check KV Storage (Temporary Cache)**

### View stored audio chunks:
```bash
cd D:\Projects\never-be-alone\universal-context\webhook-server

# List recent audio chunks
wrangler kv:key list --namespace-id=be2292279bd74f3ebfe840ce0db553d4 --prefix=audio:

# List recent transcriptions
wrangler kv:key list --namespace-id=b4130a8f406b41e08c088a3070159a1a --prefix=transcription:
```

### Get specific item:
```bash
# Get audio chunk metadata
wrangler kv:key get "audio:YOUR_UID:CHUNK_ID" --namespace-id=be2292279bd74f3ebfe840ce0db553d4

# Get transcription
wrangler kv:key get "transcription:YOUR_UID:TRANSCRIPTION_ID" --namespace-id=b4130a8f406b41e08c088a3070159a1a
```

---

## 🎯 **What to Look For**

### Successful Audio Processing:
```
✅ Received X bytes of audio from user {uid}
✅ Converted audio to WAV format
✅ Transcription completed: "{text}"
✅ Stored transcription in Supermemory
✅ Stored audio chunk {id} in KV
```

### Successful Transcription Webhook:
```
✅ Received transcription webhook
✅ Processing N segments
✅ Stored segment 1/N: "{text}"
✅ Stored transcription {id} in KV
```

### Errors to Watch For:
```
❌ Supermemory add error: {error}
❌ Groq transcription error: {error}
❌ Failed to store audio chunk in KV
❌ Audio chunk too short for transcription
```

---

## 🔍 **Quick Status Check**

Run this to check everything is working:

```bash
# 1. Check deployment
wrangler whoami

# 2. Check logs (real-time)
wrangler tail --format pretty

# 3. Check transcriptions
python view_transcriptions_simple.py

# 4. Test endpoint
curl https://never-be-alone-webhook-server.parthmaradia1507.workers.dev/health
```

---

## 📱 **Configure Omi Device**

### Omi App Settings:

1. **Audio Webhook:**
   ```
   https://never-be-alone-webhook-server.parthmaradia1507.workers.dev/webhook/audio?sample_rate=16000&uid=YOUR_UID
   ```

2. **Transcription Webhook:**
   ```
   https://never-be-alone-webhook-server.parthmaradia1507.workers.dev/webhook/transcription?uid=YOUR_UID
   ```

Replace `YOUR_UID` with your actual Omi user ID from the app.

---

## 🎤 **Test Flow**

1. **Start log monitoring**:
   ```bash
   wrangler tail --format pretty
   ```

2. **Speak into your Omi device**

3. **Watch logs** for:
   - Audio received
   - Transcription completed
   - Supermemory stored

4. **View transcriptions**:
   ```bash
   python view_transcriptions_simple.py
   ```

---

## 💡 **Pro Tips**

- **Logs expire after 24 hours** in Cloudflare (but Supermemory is permanent)
- **KV storage** keeps audio for 24h, transcriptions for 7 days
- **Supermemory** is your long-term storage - query anytime
- **Search by keywords** in Supermemory to find specific conversations

---

## 🆘 **Troubleshooting**

### No logs showing:
- Check Omi device is connected to internet
- Verify webhook URLs are correct in Omi app
- Ensure UID parameter matches your Omi user ID

### Transcriptions not appearing in Supermemory:
- Check logs for "Supermemory add error"
- Verify API key is valid
- Check MCP protocol responses

### Audio not transcribing:
- Ensure audio is at least 0.1 seconds
- Verify format: 16-bit PCM, 16000 Hz
- Check Groq API credits

---

## 📞 **Get Help**

- Check logs: `wrangler tail`
- View errors: Look for red ❌ in logs
- Test manually: Use curl or Postman to send test data
