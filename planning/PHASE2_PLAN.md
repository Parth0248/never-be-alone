# Phase 2: Transcription, Context Extraction & Agentic Layer

## Current State ✅
- Audio files streaming from Omi to GCS bucket every 10 seconds
- 165KB raw audio bytes → WAV format with headers
- Files stored: `gs://calhacks-omi-audio-files/DD_MM_YYYY_HH_MM_SS.wav`
- Cloud Run server deployed and working perfectly

## Next Phase Goals 🎯

### 1. **Audio → Text Transcription**
Convert audio files to text using Groq Whisper-large-v3

### 2. **Context Extraction & Storage**
Identify relevant context and store in Supermemory

### 3. **Agentic Layer**
Build AI agents that can understand and act on the context

---

## Architecture Design

```
┌─────────────────────────────────────────────────────────────┐
│                 Current: Audio Storage                       │
│  Omi Device → Cloud Run → GCS Bucket (.wav files)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                Phase 2: Processing Pipeline                  │
│                                                               │
│  1. GCS Cloud Function Trigger (on new file)                │
│     ↓                                                        │
│  2. Download .wav → Send to Groq Whisper-large-v3           │
│     ↓                                                        │
│  3. Get Transcription Text + Timestamps                      │
│     ↓                                                        │
│  4. Context Extraction (LLM-based)                          │
│     - Identify: Tasks, Facts, Questions, Emotions            │
│     - Extract: Named entities, Topics, Intent                │
│     ↓                                                        │
│  5. Store in Supermemory with metadata                       │
│     - Text, timestamp, user_id, context_type                │
│     - Tags, embeddings for semantic search                   │
│     ↓                                                        │
│  6. Trigger Agent Layer (if needed)                         │
│     - Task creation, reminders, actions                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 Agentic Layer                                │
│                                                               │
│  Agent Types:                                                │
│  - Memory Agent: Retrieves relevant past context            │
│  - Task Agent: Creates/manages tasks from conversations     │
│  - Question Agent: Answers questions using stored context   │
│  - Proactive Agent: Suggests actions based on patterns      │
│                                                               │
│  Framework: Fetch.ai ASI:One or Custom Agent Framework      │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Options

### Option 1: **Event-Driven Pipeline (Recommended)**
**Best for:** Real-time processing, scalability

```
GCS Bucket (new file)
    ↓ (Cloud Storage Trigger)
GCP Cloud Function
    ↓ (processes file)
Groq Whisper API → Transcription
    ↓
Claude/GPT-4 → Context Extraction
    ↓
Supermemory API → Storage
    ↓ (webhook/queue)
Agent Layer → Actions
```

**Pros:**
- Automatic processing as files arrive
- Serverless, scales automatically
- Each component can fail/retry independently
- Easy to monitor and debug

**Cons:**
- More GCP services to manage
- Need to set up Cloud Functions

---

### Option 2: **Batch Processing Worker**
**Best for:** Cost optimization, simpler setup

```
Cron Job / Worker Service
    ↓ (every 30 seconds)
Check GCS for new files
    ↓
Download unprocessed files
    ↓
Process in batches (5-10 at once)
    ↓
Store results → Supermemory
    ↓
Update processed status
```

**Pros:**
- Simpler architecture
- Easier to test locally
- Better control over processing rate
- Can batch API calls for efficiency

**Cons:**
- Slight delay (30s-1min)
- Need to track processed files
- Worker needs to stay running

---

### Option 3: **Hybrid (Cloud Function + Background Worker)**
**Best for:** Best of both worlds

```
Cloud Function (lightweight):
    - Transcribe with Groq
    - Store raw transcription
    - Add to processing queue

Background Worker (complex):
    - Context extraction
    - Agent processing
    - Long-running tasks
```

**Pros:**
- Fast initial processing
- Complex logic in controlled environment
- Can scale independently

---

## Recommended Tech Stack

### Transcription Layer
```python
# Use Groq Whisper-large-v3
from groq import Groq

client = Groq(api_key="...")
transcription = client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-large-v3",
    response_format="verbose_json",  # Get timestamps
    temperature=0.0
)
```

### Context Extraction Layer
```python
# Use Claude or GPT-4 for intelligent extraction
from anthropic import Anthropic

prompt = f"""
Analyze this conversation transcript and extract:
1. Key facts and information
2. Tasks or action items mentioned
3. Questions asked
4. Important entities (people, places, things)
5. Overall topic/intent
6. Emotional context

Transcript: {transcription_text}

Return as structured JSON.
"""

response = claude.messages.create(...)
context = json.loads(response.content)
```

### Storage in Supermemory
```python
# Using MCP Supermemory integration
supermemory.add_memory(
    content=transcription_text,
    metadata={
        'source': 'omi_audio',
        'timestamp': timestamp,
        'user_id': uid,
        'context_type': context['type'],
        'entities': context['entities'],
        'tags': context['tags'],
        'audio_file': filename
    }
)
```

### Agent Layer (Fetch.ai or Custom)
```python
# Simple agent example
class MemoryAgent:
    def retrieve_context(self, query):
        # Search Supermemory
        results = supermemory.search(query)
        return results

    def answer_question(self, question, context):
        # Use LLM with context
        response = claude.create(
            system="You have access to the user's memories",
            context=context,
            prompt=question
        )
        return response

class TaskAgent:
    def extract_tasks(self, transcription):
        # Identify action items
        tasks = llm_extract_tasks(transcription)

        for task in tasks:
            self.create_task(task)

    def create_task(self, task):
        # Add to task management system
        pass
```

---

## Implementation Plan

### Phase 2A: Core Transcription Pipeline (Week 1)
**Goal:** Audio → Text → Supermemory

```
[ ] 1. Set up Cloud Function for GCS triggers
    - Trigger on new .wav file upload
    - Function: transcribe_audio

[ ] 2. Integrate Groq Whisper API
    - Download audio from GCS
    - Send to Groq for transcription
    - Handle errors and retries

[ ] 3. Store transcriptions in Supermemory
    - Use existing MCP integration
    - Include metadata (timestamp, user_id, file)
    - Test search functionality

[ ] 4. Testing
    - Speak into Omi
    - Verify transcription accuracy
    - Check Supermemory storage
```

### Phase 2B: Context Extraction (Week 1-2)
**Goal:** Smart context understanding

```
[ ] 1. Build context extraction pipeline
    - Use Claude/GPT-4 for analysis
    - Extract: facts, tasks, questions, entities
    - Categorize conversation types

[ ] 2. Enhanced Supermemory storage
    - Rich metadata
    - Semantic tagging
    - Relationship mapping

[ ] 3. Testing
    - Various conversation types
    - Accuracy of extraction
    - Search relevance
```

### Phase 2C: Agent Layer (Week 2)
**Goal:** Intelligent actions on context

```
[ ] 1. Design agent architecture
    - Memory Agent (retrieval)
    - Task Agent (action items)
    - QA Agent (question answering)
    - Proactive Agent (suggestions)

[ ] 2. Implement core agents
    - Start with Memory + Task agents
    - Test with real conversations
    - Iterate on prompts

[ ] 3. Agent orchestration
    - When to trigger which agent
    - Agent-to-agent communication
    - User interaction flow

[ ] 4. Build simple UI/API
    - Query past conversations
    - Get task list
    - Ask questions
```

---

## Quick Start: Minimal Viable Pipeline

Let's start simple and iterate:

### Step 1: Manual Transcription Test (10 min)
```python
# test_transcription.py
# Download one audio file and transcribe it

from google.cloud import storage
from groq import Groq
import os

# Download audio
storage_client = storage.Client()
bucket = storage_client.bucket('calhacks-omi-audio-files')
blob = bucket.blob('25_10_2025_18_08_25.wav')
blob.download_to_filename('test_audio.wav')

# Transcribe
groq = Groq(api_key=os.getenv('GROQ_API_KEY'))
with open('test_audio.wav', 'rb') as f:
    transcription = groq.audio.transcriptions.create(
        file=f,
        model="whisper-large-v3",
        response_format="json"
    )

print(f"Transcription: {transcription.text}")
```

### Step 2: Store in Supermemory (10 min)
```python
# test_supermemory_storage.py
from mcp import Supermemory

supermemory = Supermemory(api_key=os.getenv('SUPERMEMORY_API_KEY'))

supermemory.add_memory(
    content=transcription.text,
    metadata={
        'source': 'omi_device',
        'timestamp': '2025-10-25T18:08:25',
        'audio_file': '25_10_2025_18_08_25.wav'
    }
)

# Verify
results = supermemory.search(transcription.text[:50])
print(f"Found in Supermemory: {results}")
```

### Step 3: Automated Processing (1 hour)
```python
# audio_processor.py
# Worker that processes all new files

import time
from google.cloud import storage
from groq import Groq
from supermemory import Supermemory

# Track processed files
processed_files = set()

def process_new_files():
    bucket = storage_client.bucket('calhacks-omi-audio-files')
    blobs = bucket.list_blobs()

    for blob in blobs:
        if blob.name not in processed_files:
            print(f"Processing {blob.name}...")

            # Download
            blob.download_to_filename('/tmp/temp.wav')

            # Transcribe
            with open('/tmp/temp.wav', 'rb') as f:
                result = groq.audio.transcriptions.create(
                    file=f,
                    model="whisper-large-v3"
                )

            # Store
            supermemory.add_memory(
                content=result.text,
                metadata={'audio_file': blob.name}
            )

            processed_files.add(blob.name)
            print(f"✅ Processed {blob.name}")

# Run continuously
while True:
    process_new_files()
    time.sleep(30)  # Check every 30 seconds
```

---

## Cost Estimation

### Groq Whisper API
- ~$0.005 per minute of audio
- 10s chunks = $0.001 per chunk
- 100 chunks/day = $0.10/day = $3/month

### GCP Cloud Functions
- Free tier: 2M invocations/month
- Easily within free tier

### Supermemory
- Free tier should cover testing
- Check pricing for production

### Total: ~$5-10/month for moderate usage

---

## Success Metrics

### Phase 2A
- [ ] 95%+ transcription accuracy
- [ ] < 5 second processing latency
- [ ] All audio files successfully transcribed

### Phase 2B
- [ ] Context extracted for 90%+ conversations
- [ ] Searchable in Supermemory within 10s
- [ ] Relevant results on searches

### Phase 2C
- [ ] Agents respond to queries
- [ ] Tasks automatically extracted
- [ ] Question answering working

---

## Next Immediate Steps

**Choose your path:**

1. **Quick Test** (30 min): Run manual transcription test
2. **Full Pipeline** (3 hours): Build automated processor
3. **Cloud Function** (2 hours): Set up event-driven processing

**I recommend:** Start with Quick Test to validate everything works, then build Full Pipeline.

---

## Questions to Answer

Before we start coding:

1. **Groq API**: Do you have API key? Need to get credits?
2. **Processing**: Real-time (Cloud Function) or Batch (Worker)?
3. **Agent Framework**: Fetch.ai ASI:One or custom Python agents?
4. **UI**: Need web interface or just API/CLI?
5. **Priorities**: Transcription → Context → Agents, or all together?

---

## Let's Build!

**My recommendation for next session:**

```
Session 1 (Now):
- Test Groq transcription manually
- Verify Supermemory integration works
- Process 5-10 audio files successfully

Session 2:
- Build automated processor
- Set up continuous processing
- Add context extraction

Session 3:
- Build first agent (Memory Agent)
- Create API for querying
- Test end-to-end flow
```

Ready to start? Which option do you want to pursue?
