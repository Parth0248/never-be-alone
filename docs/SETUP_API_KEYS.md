# Setting Up API Keys

## 1. Groq API Key (for Whisper-large-v3 Transcription)

### Get Your Key:
1. Go to: https://console.groq.com/keys
2. Sign up / Log in (free tier available)
3. Create a new API key
4. Copy the key

### Free Tier:
- Generous free credits
- Whisper-large-v3 is very affordable (~$0.005/minute)
- More than enough for testing

## 2. Supermemory API Key (for Memory Storage)

### If you have MCP Supermemory already set up:
The Supermemory MCP integration should already have your API key configured.

Check if you have it:
```bash
# Windows PowerShell
$env:SUPERMEMORY_API_KEY
```

### If you need to get a new key:
- Check Supermemory dashboard
- Or use the MCP integration directly (already configured in Claude Code)

## 3. Set Up Environment Variables

### Option A: Create .env file (recommended for this project)

```bash
# Copy the example
cp .env.example .env

# Edit .env and add your keys
```

Your `.env` file should look like:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
SUPERMEMORY_API_KEY=your_key_here
SUPERMEMORY_BASE_URL=https://api.supermemory.ai/
```

### Option B: Set in PowerShell (temporary)

```powershell
$env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxx"
$env:SUPERMEMORY_API_KEY="your_key_here"
```

## 4. Verify Setup

```bash
cd D:\Projects\never-be-alone

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install groq python-dotenv

# Test that keys are set
python -c "import os; print('GROQ_API_KEY:', 'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET')"
```

## 5. Run Transcription Test

```bash
# Make sure .env file exists with your keys
python test_transcription_pipeline.py
```

## Quick Start (Do This Now)

1. **Get Groq API Key**: Visit https://console.groq.com/keys
2. **Create .env file**: `cp .env.example .env`
3. **Add your key**: Edit .env and paste your Groq key
4. **Install packages**: `pip install groq python-dotenv`
5. **Run test**: `python test_transcription_pipeline.py`

That's it! The script will:
- ✅ Load your audio file (already downloaded)
- ✅ Transcribe with Groq Whisper-large-v3
- ✅ Show you the transcription
- ✅ Save results to JSON file
- ✅ (Optional) Store in Supermemory if key is set

## Troubleshooting

### "GROQ_API_KEY not set"
- Make sure .env file exists
- Make sure it has: `GROQ_API_KEY=your_actual_key`
- Make sure you're using python-dotenv or set env var manually

### "Module 'groq' not found"
```bash
pip install groq
```

### Still not working?
Set the key directly in PowerShell:
```powershell
$env:GROQ_API_KEY="your_key_here"
python test_transcription_pipeline.py
```
