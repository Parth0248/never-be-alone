# Local Deployment Guide with Ngrok

Quick guide to run Never-Be-Alone locally and expose it via ngrok for the Cal Hacks demo.

---

## Quick Start (5 Minutes)

### Step 1: Install Ngrok

**Windows:**
```powershell
# Download from https://ngrok.com/download
# Or use winget
winget install ngrok
```

**Mac/Linux:**
```bash
brew install ngrok
```

### Step 2: Start Your Local Server

**Windows (PowerShell):**
```powershell
cd D:\Projects\never-be-alone\agent-orchestrator
.\run_local.ps1
```

**Linux/Mac:**
```bash
cd agent-orchestrator
chmod +x run_local.sh
./run_local.sh
```

The server will start on `http://localhost:8080`

### Step 3: Test Locally

Open a new terminal and test:
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "agent-orchestrator",
  "environment": "development"
}
```

### Step 4: Expose with Ngrok

In a new terminal:
```bash
ngrok http 8080
```

You'll see output like:
```
Session Status                online
Account                       Your Account
Version                       3.x.x
Region                        United States (us)
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8080
```

Copy the `https://abc123.ngrok-free.app` URL - this is your public endpoint!

---

## Configure Omi Webhook

Update your Omi app configuration to point to your ngrok URL:
```
https://your-ngrok-url.ngrok-free.app/orchestrate
```

---

## Testing End-to-End

### Test Health
```bash
curl https://your-ngrok-url.ngrok-free.app/health
```

### Test Orchestration
```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "transcription": "Remind me tomorrow at 2pm to call mom",
    "context": {
      "uid": "demo_user",
      "timestamp": "2025-10-26T12:00:00Z",
      "source": "omi_devkit"
    }
  }'
```

---

## Monitoring

### View Server Logs
The local server terminal will show all requests and processing logs in real-time.

### View Ngrok Traffic
Open `http://localhost:4040` in your browser to see:
- All incoming requests
- Request/response details
- Replay requests
- Performance metrics

This is super helpful for debugging during the demo!

---

## Advantages of Local + Ngrok

✅ **Instant Deployment** - Running in seconds
✅ **Live Debugging** - See logs in real-time
✅ **Easy Updates** - Just restart the server
✅ **No Build Issues** - No Docker complications
✅ **Free** - Ngrok free tier is perfect for demos
✅ **Request Inspection** - Built-in dashboard at localhost:4040

---

## Production Note

For production after the hackathon, you can:
1. Use the Cloud Run deployment (once the build issues are resolved)
2. Deploy to Heroku/Railway (simpler than Cloud Run)
3. Keep using ngrok with a paid plan for persistent URLs

---

## Troubleshooting

### Port Already in Use
```powershell
# Windows: Find and kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8080 | xargs kill -9
```

### Environment Variables Not Loading
Make sure your `.env` file is in the `agent-orchestrator` directory with all required keys:
```
REKA_API_KEY=...
ASI_ONE_API_KEY=...
SUPERMEMORY_API_KEY=...
AGENTVERSE_API_KEY=...
GROQ_API_KEY=...
OMI_API_KEY=...
OMI_APP_ID=...
OMI_USER_ID=...
```

### Ngrok Connection Refused
Make sure your local server is running first (Step 2) before starting ngrok.

---

## Demo Day Checklist

- [ ] `.env` file configured with all API keys
- [ ] Local server running successfully
- [ ] Ngrok tunnel active
- [ ] Health endpoint responding
- [ ] Test request working
- [ ] Omi webhook configured to ngrok URL
- [ ] Ngrok dashboard open at localhost:4040

---

**You're ready to demo! 🚀**
