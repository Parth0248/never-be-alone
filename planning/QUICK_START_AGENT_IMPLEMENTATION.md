# Quick Start: Agent Orchestration Implementation
## From Zero to First Working Agent in 1 Week

---

## 🎯 Goal

Get your first agent working end-to-end:
**Audio from Omi → Transcription → ASI:One → Agent Action → Result**

---

## 📋 Prerequisites Checklist

- [x] Omi wearable device (DevKit 2 or Glass)
- [x] Webhook server running (already deployed to Cloud Run)
- [x] Google Cloud account with GCS bucket
- [x] Groq API key for transcription
- [x] Supermemory account
- [ ] Fetch.ai ASI:One API key
- [ ] Agentverse account
- [ ] uAgents library installed

---

## 🚀 Week 1 Implementation Plan

### Day 1-2: Set Up Event Infrastructure

#### Step 1: Create Google Cloud Pub/Sub Topic

```bash
# Set your project ID
export PROJECT_ID="calhacks-omi-audio"

# Create topic for events
gcloud pubsub topics create omi-events --project $PROJECT_ID

# Create subscription for agent orchestrator
gcloud pubsub subscriptions create omi-events-sub \
    --topic omi-events \
    --project $PROJECT_ID

# Verify
gcloud pubsub topics list --project $PROJECT_ID
```

#### Step 2: Update Webhook Server to Publish Events

```python
# Add to universal-context/webhook-server/main.py

from google.cloud import pubsub_v1

# Initialize publisher (add after Flask app initialization)
publisher = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(
    os.getenv('GCP_PROJECT_ID', 'calhacks-omi-audio'),
    'omi-events'
)

def publish_event(event_type: str, data: dict):
    """Publish event to Pub/Sub"""
    try:
        event = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        message_json = json.dumps(event)
        message_bytes = message_json.encode('utf-8')

        future = publisher.publish(TOPIC_PATH, message_bytes)
        message_id = future.result()
        logger.info(f'Published event {event_type} with message ID: {message_id}')
        return message_id
    except Exception as e:
        logger.error(f'Failed to publish event: {e}')
        return None

# Update handle_audio() function - add before return statement
        if success:
            # Publish event (ADD THIS)
            publish_event('audio_received', {
                'filename': filename,
                'uid': uid,
                'size_bytes': len(audio_data),
                'bucket': bucket_name
            })

            return jsonify({
                'success': True,
                'message': f'Audio bytes received and uploaded as {filename}',
                'filename': filename,
                'uid': uid,
                'size_bytes': len(audio_data)
            }), 200

# Update handle_transcription() function - add before return statement
        if success:
            # Publish event (ADD THIS)
            publish_event('transcription_complete', {
                'filename': filename,
                'uid': uid,
                'transcription': transcription_text,
                'length': len(transcription_text)
            })

            return jsonify({
                'success': True,
                'message': 'Transcription received and stored successfully',
                'filename': filename,
                'uid': uid,
                'length': len(transcription_text)
            }), 200
```

#### Step 3: Add Pub/Sub Dependency

```bash
# Update requirements.txt
echo "google-cloud-pubsub==2.23.1" >> universal-context/webhook-server/requirements.txt

# Install locally for testing
cd universal-context/webhook-server
pip install google-cloud-pubsub
```

#### Step 4: Test Event Publishing

```python
# test_event_publishing.py
from google.cloud import pubsub_v1
import json
from datetime import datetime

project_id = "calhacks-omi-audio"
topic_id = "omi-events"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Test event
event = {
    'event_type': 'transcription_complete',
    'data': {
        'uid': 'test_user',
        'transcription': 'Remind me to call mom tomorrow at 3pm',
        'timestamp': datetime.now().isoformat()
    }
}

future = publisher.publish(topic_path, json.dumps(event).encode('utf-8'))
print(f'Published message ID: {future.result()}')
```

---

### Day 3-4: Set Up Fetch.ai & Create First Agent

#### Step 1: Sign Up for Fetch.ai Services

1. **ASI:One Account**
   - Go to https://as1.ai
   - Create account
   - Navigate to API Keys section
   - Generate API key → Save as `ASI_ONE_API_KEY`

2. **Agentverse Account**
   - Go to https://agentverse.ai
   - Create account
   - Link to ASI:One account

#### Step 2: Install uAgents Framework

```bash
# Create agent development directory
mkdir -p universal-context/agents
cd universal-context/agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install uAgents and dependencies
pip install uagents requests flask python-dotenv

# Create requirements.txt
cat > requirements.txt << EOF
uagents==0.14.0
requests==2.31.0
flask==3.0.0
python-dotenv==1.0.1
openai==1.54.0
anthropic==0.39.0
EOF
```

#### Step 3: Create Your First Agent - Task Classifier

```python
# universal-context/agents/task_classifier_agent.py

from uagents import Agent, Context, Protocol, Model
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# Define message models
class TranscriptionRequest(Model):
    uid: str
    transcription: str
    timestamp: str
    context: dict = {}

class TaskClassification(Model):
    category: str  # command, question, observation, conversation
    intent: str    # create_reminder, send_email, search_info, etc.
    entities: dict
    confidence: float
    suggested_agent: str  # Which agent should handle this

# Initialize OpenAI for classification (or use Claude)
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Create the agent
task_classifier = Agent(
    name="task-classifier",
    seed=os.getenv('AGENT_SEED', 'task_classifier_seed_phrase_12345'),
    port=8001,
    endpoint=["http://localhost:8001/submit"],
)

# Create protocol for handling messages
classification_protocol = Protocol("TaskClassification")

def classify_transcription(transcription: str) -> dict:
    """Use LLM to classify the transcription"""
    system_prompt = """You are a task classifier for a personal AI assistant. Analyze the transcription and classify it.

Categories:
- command: User wants something done (create reminder, send email, etc.)
- question: User asking for information
- observation: User noting something for memory
- conversation: General conversation, no action needed

Extract:
- intent: Specific action (create_reminder, send_email, search_info, log_observation, etc.)
- entities: People, dates, times, locations, etc.
- suggested_agent: Which specialized agent should handle this (calendar_agent, email_agent, context_agent, etc.)

Respond with JSON only."""

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transcription: {transcription}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    return result

@classification_protocol.on_message(model=TranscriptionRequest)
async def handle_transcription(ctx: Context, sender: str, msg: TranscriptionRequest):
    """Receive transcription and classify it"""
    ctx.logger.info(f"Received transcription from {msg.uid}: {msg.transcription[:50]}...")

    try:
        # Classify the transcription
        classification = classify_transcription(msg.transcription)

        # Add confidence score
        classification['confidence'] = 0.85  # Could be calculated from LLM

        # Log the classification
        ctx.logger.info(f"Classification: {classification['category']} - {classification['intent']}")

        # Send classification result back
        response = TaskClassification(
            category=classification.get('category', 'unknown'),
            intent=classification.get('intent', 'unknown'),
            entities=classification.get('entities', {}),
            confidence=classification.get('confidence', 0.5),
            suggested_agent=classification.get('suggested_agent', 'none')
        )

        await ctx.send(sender, response)

    except Exception as e:
        ctx.logger.error(f"Error classifying transcription: {e}")

# Include protocol in agent
task_classifier.include(classification_protocol)

# Startup message
@task_classifier.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Task Classifier Agent started")
    ctx.logger.info(f"Agent address: {task_classifier.address}")

if __name__ == "__main__":
    task_classifier.run()
```

#### Step 4: Test Your Agent Locally

```python
# test_agent_local.py
import asyncio
from uagents import Agent, Context, Model
from task_classifier_agent import TranscriptionRequest, TaskClassification

# Create a test client
test_client = Agent(name="test_client", seed="test_seed")

@test_client.on_event("startup")
async def send_test_message(ctx: Context):
    # Address of task classifier (get from console output)
    classifier_address = "agent1q..." # Replace with actual address

    test_transcription = TranscriptionRequest(
        uid="test_user",
        transcription="Remind me to call mom tomorrow at 3pm",
        timestamp="2025-10-25T14:30:00Z"
    )

    await ctx.send(classifier_address, test_transcription)
    ctx.logger.info("Sent test transcription")

@test_client.on_message(model=TaskClassification)
async def handle_classification(ctx: Context, sender: str, msg: TaskClassification):
    ctx.logger.info(f"Received classification:")
    ctx.logger.info(f"  Category: {msg.category}")
    ctx.logger.info(f"  Intent: {msg.intent}")
    ctx.logger.info(f"  Entities: {msg.entities}")
    ctx.logger.info(f"  Suggested Agent: {msg.suggested_agent}")

if __name__ == "__main__":
    test_client.run()
```

#### Step 5: Run and Test

```bash
# Terminal 1: Start task classifier agent
cd universal-context/agents
source venv/bin/activate
python task_classifier_agent.py

# Terminal 2: Send test message
python test_agent_local.py
```

---

### Day 5-6: Create Agent Orchestrator Service

#### Step 1: Build the Orchestrator

```python
# universal-context/agent-orchestrator/main.py

from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from uagents import Agent, Context, Model
from uagents.query import query
import threading

load_dotenv()

app = Flask(__name__)

# Pub/Sub subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    os.getenv('GCP_PROJECT_ID', 'calhacks-omi-audio'),
    'omi-events-sub'
)

# Agent addresses (register your agents here)
AGENT_ADDRESSES = {
    'task_classifier': os.getenv('TASK_CLASSIFIER_ADDRESS'),
    'calendar_agent': os.getenv('CALENDAR_AGENT_ADDRESS'),
    'context_agent': os.getenv('CONTEXT_AGENT_ADDRESS'),
}

class TranscriptionRequest(Model):
    uid: str
    transcription: str
    timestamp: str
    context: dict = {}

def process_event(event_data):
    """Process incoming event from Pub/Sub"""
    event_type = event_data.get('event_type')
    data = event_data.get('data')

    print(f"Processing event: {event_type}")

    if event_type == 'transcription_complete':
        handle_transcription(data)
    elif event_type == 'audio_received':
        handle_audio(data)

def handle_transcription(data):
    """Handle transcription complete event"""
    transcription = data.get('transcription')
    uid = data.get('uid')
    timestamp = data.get('timestamp', datetime.now().isoformat())

    print(f"Transcription from {uid}: {transcription}")

    # Send to task classifier agent
    asyncio.run(send_to_classifier(uid, transcription, timestamp))

async def send_to_classifier(uid, transcription, timestamp):
    """Send transcription to task classifier agent"""
    classifier_address = AGENT_ADDRESSES['task_classifier']

    if not classifier_address:
        print("Task classifier address not configured")
        return

    request = TranscriptionRequest(
        uid=uid,
        transcription=transcription,
        timestamp=timestamp
    )

    try:
        # Query the agent
        response = await query(
            destination=classifier_address,
            message=request,
            timeout=15.0
        )

        print(f"Classification result: {response}")

        # Based on classification, route to appropriate agent
        if response.intent == 'create_reminder':
            await send_to_calendar_agent(uid, response)
        elif response.intent == 'search_info':
            await send_to_context_agent(uid, response)

    except Exception as e:
        print(f"Error sending to classifier: {e}")

async def send_to_calendar_agent(uid, classification):
    """Send to calendar agent for reminder creation"""
    # Implementation for calendar agent
    print(f"Would send to calendar agent: {classification}")

async def send_to_context_agent(uid, classification):
    """Send to context agent for information retrieval"""
    # Implementation for context agent
    print(f"Would send to context agent: {classification}")

def handle_audio(data):
    """Handle audio received event"""
    # For now, just log. Later can trigger transcription
    print(f"Audio received: {data.get('filename')}")

def pubsub_callback(message):
    """Callback for Pub/Sub messages"""
    try:
        event_data = json.loads(message.data.decode('utf-8'))
        process_event(event_data)
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()

def start_subscriber():
    """Start Pub/Sub subscriber in background thread"""
    streaming_pull_future = subscriber.subscribe(
        subscription_path,
        callback=pubsub_callback
    )

    print(f"Listening for messages on {subscription_path}")

    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        print(f"Subscriber error: {e}")

# Flask endpoints for testing
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'agent-orchestrator'})

@app.route('/test-classification', methods=['POST'])
def test_classification():
    """Test endpoint to manually trigger classification"""
    data = request.get_json()
    transcription = data.get('transcription')
    uid = data.get('uid', 'test_user')

    asyncio.run(send_to_classifier(uid, transcription, datetime.now().isoformat()))

    return jsonify({'success': True})

if __name__ == '__main__':
    # Start Pub/Sub subscriber in background
    subscriber_thread = threading.Thread(target=start_subscriber, daemon=True)
    subscriber_thread.start()

    # Start Flask app
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
```

#### Step 2: Environment Configuration

```bash
# universal-context/agent-orchestrator/.env
GCP_PROJECT_ID=calhacks-omi-audio
TASK_CLASSIFIER_ADDRESS=agent1q...  # Get from task classifier startup
OPENAI_API_KEY=sk-...
PORT=8080
```

---

### Day 7: End-to-End Testing

#### Test Flow

```bash
# Terminal 1: Run task classifier agent
cd universal-context/agents
python task_classifier_agent.py

# Terminal 2: Run orchestrator
cd universal-context/agent-orchestrator
python main.py

# Terminal 3: Publish test event
python << EOF
from google.cloud import pubsub_v1
import json
from datetime import datetime

project_id = "calhacks-omi-audio"
topic_id = "omi-events"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

event = {
    'event_type': 'transcription_complete',
    'data': {
        'uid': 'test_user',
        'transcription': 'Remind me to call mom tomorrow at 3pm',
        'timestamp': datetime.now().isoformat()
    }
}

future = publisher.publish(topic_path, json.dumps(event).encode('utf-8'))
print(f'Published message ID: {future.result()}')
EOF
```

#### Expected Output

```
Terminal 1 (Task Classifier):
INFO: Received transcription from test_user: Remind me to call mom tomorrow at 3pm
INFO: Classification: command - create_reminder

Terminal 2 (Orchestrator):
Processing event: transcription_complete
Transcription from test_user: Remind me to call mom tomorrow at 3pm
Classification result: {'category': 'command', 'intent': 'create_reminder', ...}
```

---

## 🎉 Success Criteria

After Week 1, you should have:

- [x] Event publishing from webhook server
- [x] Pub/Sub topic & subscription working
- [x] Task classifier agent running locally
- [x] Agent orchestrator service running
- [x] End-to-end flow: Pub/Sub → Orchestrator → Agent → Response

---

## 🔄 Next Steps (Week 2)

1. **Deploy Agents to Agentverse**
   - Register agents on Agentverse platform
   - Get public agent addresses
   - Test remote agent communication

2. **Build Calendar Agent**
   - Integrate Google Calendar API
   - Create reminders from classified intents

3. **Deploy Orchestrator to Cloud Run**
   - Containerize orchestrator service
   - Deploy alongside webhook server

4. **Connect Real Omi Device**
   - Update webhook URL to include orchestrator
   - Test with actual audio from device

---

## 🐛 Troubleshooting

### Issue: Agent not receiving messages
- Check agent address is correct
- Verify ports are open (8001, 8002, etc.)
- Check firewall settings

### Issue: Pub/Sub not delivering messages
- Verify subscription exists: `gcloud pubsub subscriptions list`
- Check IAM permissions for service account
- Look at Pub/Sub dashboard in GCP console

### Issue: Classification returning poor results
- Try different LLM (GPT-4 vs Claude vs Gemini)
- Improve system prompt with examples
- Add few-shot examples in prompt

---

## 📝 Testing Checklist

- [ ] Pub/Sub topic created
- [ ] Events published from webhook server
- [ ] Task classifier agent starts successfully
- [ ] Agent receives test message
- [ ] Classification returns expected format
- [ ] Orchestrator subscribes to Pub/Sub
- [ ] Orchestrator routes to correct agent
- [ ] End-to-end test passes

---

## 🎓 Learning Resources

- **uAgents Tutorial**: https://fetch.ai/docs/examples/uagents
- **Pub/Sub Python Client**: https://cloud.google.com/pubsub/docs/quickstart-client-libraries
- **Agent Communication**: https://docs.asi1.ai/documentation/tutorials/agent-chat-protocol

---

**Ready to build? Start with Day 1 and let's ship this! 🚀**
