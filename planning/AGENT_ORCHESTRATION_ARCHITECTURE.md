# Agent Orchestration Architecture: Never Be Alone
## Multi-Layer AI System with Fetch.ai Integration

---

## 🎯 Vision

Transform passive stimulus capture (audio/images from Omi wearables) into an **active agentic system** that:
1. **Understands** what the user is requesting
2. **Decides** which specialized agents should handle the task
3. **Delegates** work to appropriate agents
4. **Coordinates** multi-agent workflows
5. **Integrates** with desktop workflows (Claude, automation tools)

---

## 🏗️ Current Architecture (Phase 1 - Complete)

```
┌─────────────────────────────────────────────────────────────────┐
│                    STIMULUS CAPTURE LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  Omi Wearable (DevKit 2/Glass)                                  │
│    • Audio: Raw PCM @ 16kHz, 16-bit, mono                       │
│    • Images: JPG/PNG                                             │
│    • Frequency: Every 5-10 seconds                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Webhook POST
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Flask Webhook Server (Cloud Run)                               │
│    • POST /audio?uid=USER_ID                                    │
│    • POST /transcription?uid=USER_ID                            │
│    • Converts PCM → WAV                                          │
│    • Timestamps & validates data                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Google Cloud Storage                                            │
│    • Bucket: calhacks-omi-audio-files                           │
│    • Audio: DD_MM_YYYY_HH_MM_SS.wav                             │
│    • Transcriptions: transcriptions/{uid}/YYYY/MM/DD/...        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER (Manual)                     │
├─────────────────────────────────────────────────────────────────┤
│  Groq Whisper API                                                │
│    • Model: whisper-large-v3                                    │
│    • Transcription with timestamps                              │
│    • Language detection                                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CONTEXT STORAGE                                │
├─────────────────────────────────────────────────────────────────┤
│  Supermemory (Universal Context)                                │
│    • Full-text & semantic search                                │
│    • Metadata indexing                                           │
│    • MCP integration for Claude                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Proposed Architecture (Phase 2-3: Agent Orchestration)

```
┌─────────────────────────────────────────────────────────────────┐
│                    STIMULUS CAPTURE LAYER                       │
│  Omi Wearable → Audio + Images                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│               INGESTION & PREPROCESSING LAYER                   │
│  Flask Webhook Server                                            │
│    • Audio → WAV conversion                                     │
│    • Image validation                                            │
│    • Event emission to orchestrator                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ├────────────────┬────────────────┬───────────────┐
                  ▼                ▼                ▼               ▼
        ┌─────────────────┐  ┌──────────┐  ┌──────────────┐  ┌──────┐
        │   GCS Storage   │  │  Groq    │  │ Supermemory  │  │ NEW: │
        │  (Raw Files)    │  │ Whisper  │  │  (Context)   │  │ Agent│
        └─────────────────┘  └──────────┘  └──────────────┘  │Queue │
                                                               └──┬───┘
                                                                  │
╔═════════════════════════════════════════════════════════════════╧═══╗
║                    🤖 AGENT ORCHESTRATION LAYER 🤖                  ║
║                  (Fetch.ai ASI:One + Agentverse)                    ║
╚═════════════════════════════════════════════════════════════════════╝
                                    │
                  ┌─────────────────┴──────────────────┐
                  ▼                                     ▼
    ┌──────────────────────────────────┐  ┌────────────────────────────┐
    │     ASI:One (Router)             │  │   Agentverse (Registry)    │
    │  • Intent Classification         │  │  • Agent Discovery         │
    │  • Natural Language Understanding│  │  • Agent Marketplace       │
    │  • Request Routing               │  │  • Service Catalog         │
    │  • LLM-Powered Decision Making   │  │  • Agent Versioning        │
    └──────────────┬───────────────────┘  └────────────────────────────┘
                   │                                    ▲
                   │  ┌─────────────────────────────────┘
                   │  │  Chat Protocol Communication
                   ▼  ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │              SPECIALIZED AGENT LAYER                             │
    ├──────────────────────────────────────────────────────────────────┤
    │  🎯 Task Classification Agent                                    │
    │    • Analyzes transcription for action items                     │
    │    • Identifies: reminders, questions, commands, observations    │
    │                                                                   │
    │  📧 Communication Agent                                          │
    │    • "Send email to John about the meeting"                      │
    │    • "Reply to Sarah's message"                                  │
    │    • Drafts messages, schedules sends                            │
    │                                                                   │
    │  🗓️ Calendar & Task Agent                                        │
    │    • "Remind me to call mom tomorrow"                            │
    │    • "Schedule meeting with team next week"                      │
    │    • Integrates with Google Calendar, Notion, etc.               │
    │                                                                   │
    │  💡 Knowledge & Research Agent                                   │
    │    • "What was that book John mentioned last week?"              │
    │    • "Look up information about quantum computing"               │
    │    • Searches Supermemory + web                                  │
    │                                                                   │
    │  🎨 Creative & Content Agent                                     │
    │    • "Write a poem about this moment"                            │
    │    • "Generate an image of what I'm describing"                  │
    │    • Creates content based on context                            │
    │                                                                   │
    │  🏠 Smart Home & IoT Agent                                       │
    │    • "Turn on living room lights"                                │
    │    • "Set thermostat to 72 degrees"                              │
    │    • Controls connected devices                                  │
    │                                                                   │
    │  📊 Analytics & Insights Agent                                   │
    │    • Analyzes patterns in conversations                          │
    │    • "How much time did I spend in meetings this week?"          │
    │    • Generates life insights                                     │
    │                                                                   │
    │  🔍 Context Retrieval Agent                                      │
    │    • Fetches relevant memories from Supermemory                  │
    │    • Enriches current context with past information              │
    │    • Provides conversation history                               │
    └──────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │              EXECUTION & INTEGRATION LAYER                       │
    ├──────────────────────────────────────────────────────────────────┤
    │  Desktop Integration Hub                                         │
    │    • Claude MCP Server (running locally)                         │
    │    • Python automation scripts                                   │
    │    • Keyboard/mouse control (pyautogui)                          │
    │    • Application API integrations                                │
    │                                                                   │
    │  External API Integrations                                       │
    │    • Email (Gmail API, SendGrid)                                 │
    │    • Calendar (Google Calendar, Outlook)                         │
    │    • Task Management (Notion, Todoist, Trello)                   │
    │    • Communication (Slack, Discord, SMS via Twilio)              │
    │    • Smart Home (HomeAssistant, Philips Hue, SmartThings)        │
    │    • Web Services (Zapier, IFTTT for long-tail integrations)     │
    └──────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                   FEEDBACK & MONITORING                          │
    ├──────────────────────────────────────────────────────────────────┤
    │  • Action completion status                                      │
    │  • Agent performance metrics                                     │
    │  • User feedback collection                                      │
    │  • System health monitoring                                      │
    │  • Logging to Supermemory (completed actions as memories)        │
    └──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: From Stimulus to Action

### Example Scenario: "Remind me to call mom tomorrow at 3pm"

```
1. CAPTURE
   Omi Device captures audio: "Remind me to call mom tomorrow at 3pm"
   ↓

2. INGESTION
   Webhook receives PCM audio → converts to WAV → stores in GCS
   ↓

3. TRANSCRIPTION
   Groq Whisper transcribes: "Remind me to call mom tomorrow at 3pm"
   ↓

4. CONTEXT ENRICHMENT
   Supermemory stores transcription + metadata
   ↓

5. AGENT ORCHESTRATION (NEW!)
   a. Event published to Agent Queue:
      {
        "event_type": "transcription_complete",
        "content": "Remind me to call mom tomorrow at 3pm",
        "timestamp": "2025-10-25T14:30:00Z",
        "uid": "user123",
        "context": {
          "location": "home",
          "recent_memories": [...]
        }
      }

   b. ASI:One receives event:
      - Analyzes natural language
      - Identifies intent: "CREATE_REMINDER"
      - Extracts entities:
        * Action: "call"
        * Person: "mom"
        * Time: "tomorrow at 3pm"

   c. ASI:One routes to Calendar & Task Agent:
      Chat Protocol Message:
      {
        "type": "ChatMessage",
        "content": {
          "text": "Create reminder: Call mom",
          "structured_data": {
            "action": "create_reminder",
            "title": "Call mom",
            "datetime": "2025-10-26T15:00:00Z",
            "uid": "user123"
          }
        }
      }

6. AGENT EXECUTION
   Calendar & Task Agent:
   - Receives request via Chat Protocol
   - Determines best calendar (Google Calendar)
   - Creates calendar event:
     * Title: "Call mom"
     * Time: Tomorrow 3pm
     * Type: Reminder with notification
   - Sends ChatAcknowledgement back to ASI:One

7. DESKTOP INTEGRATION (Optional)
   If user is at desktop:
   - MCP server receives notification
   - Shows desktop notification: "Reminder created: Call mom tomorrow at 3pm"
   - Option to: "Open Calendar" or "Dismiss"

8. FEEDBACK LOOP
   - Action logged to Supermemory:
     "User requested reminder to call mom, successfully created for tomorrow 3pm"
   - Agent performance tracked
   - User can say "Did you create that reminder?" → Context agent retrieves this memory
```

---

## 🔧 Implementation Plan

### Phase 2A: Agent Queue & Event System (Week 1-2)

**Objective**: Add event-driven architecture to existing webhook server

**Components to Build**:

1. **Event Queue System**
   - Technology: Redis Pub/Sub or Google Cloud Pub/Sub
   - Location: New service or extend existing webhook server
   - Events to publish:
     * `audio_received`
     * `transcription_complete`
     * `image_received`
     * `context_updated`

   ```python
   # Add to main.py
   from google.cloud import pubsub_v1

   publisher = pubsub_v1.PublisherClient()
   topic_path = publisher.topic_path('calhacks-omi-audio', 'omi-events')

   def publish_event(event_type, data):
       message = {
           'event_type': event_type,
           'data': data,
           'timestamp': datetime.now().isoformat()
       }
       future = publisher.publish(topic_path, json.dumps(message).encode('utf-8'))
       return future.result()
   ```

2. **Automated Transcription Pipeline**
   - Cloud Function triggered by GCS uploads
   - Automatically transcribe new audio files
   - Publish `transcription_complete` event

   ```python
   # cloud_function_transcribe.py
   def transcribe_audio(event, context):
       bucket_name = event['bucket']
       file_name = event['name']

       # Download from GCS
       # Transcribe with Groq
       # Store in Supermemory
       # Publish event to agent queue
   ```

3. **Update Webhook Server**
   - Add event publishing to `/audio` and `/transcription` endpoints
   - Emit events after successful processing

   ```python
   # In handle_audio()
   if success:
       publish_event('audio_received', {
           'filename': filename,
           'uid': uid,
           'size_bytes': len(audio_data)
       })
   ```

**Deliverables**:
- [ ] Redis/Pub/Sub setup
- [ ] Event publisher integrated into webhook server
- [ ] Cloud Function for auto-transcription
- [ ] Event schema documentation

---

### Phase 2B: ASI:One Integration (Week 3-4)

**Objective**: Connect event queue to Fetch.ai ASI:One for intent routing

**Components to Build**:

1. **Agent Orchestrator Service**
   - New Python service (Flask or FastAPI)
   - Subscribes to event queue
   - Forwards events to ASI:One
   - Location: `universal-context/agent-orchestrator/`

   ```python
   # agent_orchestrator/main.py
   from google.cloud import pubsub_v1
   import requests
   from asi_one_client import ASIOneClient

   asi_client = ASIOneClient(api_key=os.getenv('ASI_ONE_API_KEY'))

   def process_event(message):
       event_data = json.loads(message.data)

       if event_data['event_type'] == 'transcription_complete':
           # Send to ASI:One for intent classification
           response = asi_client.route_message(
               user_id=event_data['data']['uid'],
               message=event_data['data']['transcription'],
               context={
                   'timestamp': event_data['timestamp'],
                   'source': 'omi_wearable'
               }
           )

           # ASI:One returns which agent(s) to invoke
           for agent_task in response['agent_tasks']:
               invoke_agent(agent_task)
   ```

2. **ASI:One API Client**
   - Wrapper for ASI:One API
   - Handles authentication
   - Manages Chat Protocol communication

   ```python
   # agent_orchestrator/asi_one_client.py
   class ASIOneClient:
       def __init__(self, api_key):
           self.api_key = api_key
           self.base_url = "https://api.asi1.ai"

       def route_message(self, user_id, message, context=None):
           """Send message to ASI:One for routing"""
           response = requests.post(
               f"{self.base_url}/v1/route",
               headers={"Authorization": f"Bearer {self.api_key}"},
               json={
                   "user_id": user_id,
                   "message": message,
                   "context": context
               }
           )
           return response.json()
   ```

3. **Agentverse Registration**
   - Create account on Agentverse
   - Register initial agents
   - Configure agent capabilities and intents

**Deliverables**:
- [ ] Agent Orchestrator service deployed
- [ ] ASI:One account & API keys
- [ ] Basic agents registered in Agentverse
- [ ] Event → ASI:One → Agent flow working

---

### Phase 2C: Build First Specialized Agents (Week 5-6)

**Objective**: Create 3-5 functional agents using uAgents framework

**Priority Agents**:

1. **Task Classification Agent**
   - Analyzes transcriptions
   - Categorizes: command, question, observation, etc.
   - Extracts entities (people, dates, actions)

   ```python
   # agents/task_classifier.py
   from uagents import Agent, Context, Protocol
   from uagents.models import Model
   from asi_one.chat_protocol import ChatMessage, ChatAcknowledgement

   class TaskRequest(Model):
       transcription: str
       uid: str
       timestamp: str

   class TaskClassification(Model):
       category: str  # command, question, observation
       intent: str    # create_reminder, search_info, etc.
       entities: dict
       confidence: float

   task_agent = Agent(
       name="task-classifier",
       seed="your-seed-phrase",
       endpoint=["http://your-server.com/task-classifier"]
   )

   chat_protocol = Protocol()

   @chat_protocol.on_message(model=ChatMessage)
   async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
       # Use Claude/GPT-4 to analyze transcription
       classification = classify_task(msg.content.text)

       # Send acknowledgement
       await ctx.send(sender, ChatAcknowledgement(
           message_id=msg.message_id,
           status="processed"
       ))

       # Return classification
       await ctx.send(sender, TaskClassification(**classification))

   task_agent.include(chat_protocol)
   ```

2. **Calendar & Reminder Agent**
   - Creates calendar events
   - Sets reminders
   - Integrates with Google Calendar API

   ```python
   # agents/calendar_agent.py
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   from uagents import Agent, Context, Protocol

   calendar_agent = Agent(name="calendar-agent")

   @calendar_agent.on_message(model=CreateReminderRequest)
   async def create_reminder(ctx: Context, sender: str, msg: CreateReminderRequest):
       # Google Calendar API integration
       service = build('calendar', 'v3', credentials=get_credentials())

       event = {
           'summary': msg.title,
           'start': {'dateTime': msg.datetime},
           'end': {'dateTime': msg.datetime},
           'reminders': {
               'useDefault': False,
               'overrides': [{'method': 'popup', 'minutes': 0}]
           }
       }

       created_event = service.events().insert(
           calendarId='primary',
           body=event
       ).execute()

       # Send success message back
       await ctx.send(sender, ReminderCreatedResponse(
           event_id=created_event['id'],
           success=True
       ))
   ```

3. **Context Retrieval Agent**
   - Queries Supermemory
   - Enriches current context with relevant memories
   - Answers "what did I say about X?" questions

   ```python
   # agents/context_agent.py
   from supermemory import Supermemory
   from uagents import Agent, Context

   context_agent = Agent(name="context-retrieval")
   sm = Supermemory(api_key=os.getenv('SUPERMEMORY_API_KEY'))

   @context_agent.on_message(model=ContextQuery)
   async def search_context(ctx: Context, sender: str, msg: ContextQuery):
       # Search Supermemory
       results = sm.search(
           query=msg.question,
           user_id=msg.uid,
           limit=5
       )

       # Format and return results
       await ctx.send(sender, ContextResponse(
           results=results,
           context_found=len(results) > 0
       ))
   ```

**Deliverables**:
- [ ] 3 agents developed and tested
- [ ] Agents registered in Agentverse
- [ ] Agent communication via Chat Protocol working
- [ ] End-to-end test: audio → transcription → agent action

---

### Phase 3A: Desktop Integration - MCP Server (Week 7-8)

**Objective**: Enable agents to interact with desktop environment

**Components to Build**:

1. **Local MCP Server**
   - Runs on user's desktop
   - Receives agent requests
   - Executes desktop actions
   - Location: `desktop-integration/mcp-server/`

   ```python
   # desktop-integration/mcp-server/main.py
   from flask import Flask, request, jsonify
   import pyautogui
   import subprocess
   import webbrowser

   app = Flask(__name__)

   @app.route('/execute', methods=['POST'])
   def execute_action():
       """Execute desktop action from agent"""
       data = request.get_json()
       action_type = data.get('action_type')

       if action_type == 'open_url':
           webbrowser.open(data['url'])
       elif action_type == 'notification':
           show_notification(data['title'], data['message'])
       elif action_type == 'open_app':
           subprocess.Popen(data['app_path'])
       elif action_type == 'keyboard':
           pyautogui.write(data['text'])

       return jsonify({'success': True})

   def show_notification(title, message):
       """Show desktop notification"""
       if platform.system() == 'Windows':
           from win10toast import ToastNotifier
           toaster = ToastNotifier()
           toaster.show_toast(title, message, duration=10)
       elif platform.system() == 'Darwin':  # macOS
           os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
       elif platform.system() == 'Linux':
           os.system(f'notify-send "{title}" "{message}"')
   ```

2. **Agent → Desktop Bridge**
   - Connects Agentverse agents to local MCP server
   - Handles authentication & security
   - Uses WebSocket or ngrok for local access

   ```python
   # agents/desktop_integration_agent.py
   import websockets
   from uagents import Agent, Context

   desktop_agent = Agent(name="desktop-integration")

   # WebSocket connection to user's local MCP server
   desktop_connections = {}  # uid → websocket connection

   @desktop_agent.on_message(model=DesktopActionRequest)
   async def execute_desktop_action(ctx: Context, sender: str, msg: DesktopActionRequest):
       # Get user's desktop connection
       ws = desktop_connections.get(msg.uid)

       if ws:
           await ws.send(json.dumps({
               'action_type': msg.action_type,
               'data': msg.data
           }))

           # Wait for response
           response = await ws.recv()
           await ctx.send(sender, DesktopActionResponse(**json.loads(response)))
       else:
           await ctx.send(sender, DesktopActionResponse(
               success=False,
               error="Desktop not connected"
           ))
   ```

3. **Claude MCP Integration**
   - Claude can already access Supermemory via MCP
   - Add new MCP tools for agent actions
   - Allow Claude to trigger agent workflows

   ```json
   # claude-mcp-config.json
   {
     "mcpServers": {
       "supermemory": {
         "command": "npx",
         "args": ["-y", "@supermemory/mcp-server"]
       },
       "never-be-alone": {
         "command": "python",
         "args": ["desktop-integration/mcp-server/main.py"]
       }
     }
   }
   ```

**Deliverables**:
- [ ] Local MCP server running on desktop
- [ ] Agent can trigger desktop notifications
- [ ] Agent can open URLs/apps
- [ ] Claude can invoke agent actions
- [ ] Security: authentication tokens, rate limiting

---

### Phase 3B: External API Integrations (Week 9-10)

**Objective**: Connect agents to external services

**Integrations to Build**:

1. **Email Agent** (Gmail API)
   ```python
   # agents/email_agent.py
   from googleapiclient.discovery import build

   @email_agent.on_message(model=SendEmailRequest)
   async def send_email(ctx: Context, sender: str, msg: SendEmailRequest):
       service = build('gmail', 'v1', credentials=get_credentials())

       message = create_message(
           to=msg.recipient,
           subject=msg.subject,
           body=msg.body
       )

       sent = service.users().messages().send(
           userId='me',
           body=message
       ).execute()
   ```

2. **Smart Home Agent** (HomeAssistant API)
   ```python
   # agents/smart_home_agent.py
   import homeassistant_api as ha

   @smart_home_agent.on_message(model=SmartHomeCommand)
   async def control_device(ctx: Context, sender: str, msg: SmartHomeCommand):
       client = ha.Client(os.getenv('HA_URL'), os.getenv('HA_TOKEN'))

       if msg.command == 'turn_on':
           client.trigger_service('light', 'turn_on', entity_id=msg.device_id)
   ```

3. **Zapier Integration** (for long-tail services)
   ```python
   # agents/zapier_agent.py
   @zapier_agent.on_message(model=ZapierTrigger)
   async def trigger_zap(ctx: Context, sender: str, msg: ZapierTrigger):
       response = requests.post(
           msg.webhook_url,
           json=msg.data
       )
   ```

**Deliverables**:
- [ ] Email agent (Gmail integration)
- [ ] Smart home agent (1-2 platforms)
- [ ] Zapier/IFTTT integration for extensibility
- [ ] OAuth flow for user authentication

---

### Phase 4: Advanced Features (Week 11-12)

**Objective**: Multi-agent coordination, proactive actions, learning

**Features to Build**:

1. **Multi-Agent Workflows**
   - Task Classification → Context Retrieval → Calendar Agent
   - Sequential and parallel agent execution
   - Error handling and retries

2. **Proactive Agent Actions**
   - Agents analyze patterns and suggest actions
   - "You usually call mom on Sundays, should I remind you?"
   - "You mentioned reading this book 3 times, should I order it?"

3. **User Feedback Loop**
   - User confirms/rejects agent actions
   - Agents learn from feedback
   - Improve routing and intent classification

4. **Visual Dashboard**
   - Web UI to view agent activity
   - See what agents are doing
   - Override/cancel agent actions

**Deliverables**:
- [ ] Multi-agent workflow engine
- [ ] Proactive action system
- [ ] Feedback collection mechanism
- [ ] Admin dashboard (optional)

---

## 🔐 Security Considerations

1. **Authentication & Authorization**
   - User authentication for webhook endpoints
   - API key management (rotate regularly)
   - Agent-to-agent authentication via Chat Protocol

2. **Data Privacy**
   - Encrypt audio/transcriptions at rest
   - Secure transmission (HTTPS, TLS)
   - User consent for agent actions

3. **Desktop Access**
   - Local MCP server: localhost only by default
   - Optional: ngrok with authentication tokens
   - Rate limiting on agent actions

4. **Agent Permissions**
   - Agents request permissions for actions
   - User approves high-risk actions (emails, payments)
   - Audit log of all agent actions

---

## 💰 Cost Estimation

### Monthly Costs (Moderate Usage)

| Component | Cost | Notes |
|-----------|------|-------|
| Google Cloud Run | Free | Free tier covers typical usage |
| Google Cloud Storage | $0.50 | ~1GB audio files |
| Google Cloud Pub/Sub | $0.40 | ~10K messages/month |
| Groq Whisper API | $5.00 | ~1000 minutes/month |
| Supermemory | Free | Free tier (10K memories) |
| Fetch.ai Agentverse | $0-20 | Depends on agent usage |
| Gmail/Calendar API | Free | Google Workspace APIs |
| Miscellaneous APIs | $5-10 | Twilio SMS, other services |
| **Total** | **~$15-30** | Per user per month |

### Infrastructure Scaling

- **Low usage** (1-10 users): ~$20/month
- **Medium usage** (10-100 users): ~$100-200/month
- **High usage** (100-1000 users): ~$500-1000/month

---

## 🎯 Success Metrics

### Phase 2 Success Criteria
- [ ] 90%+ transcription accuracy
- [ ] <5s latency from audio to agent action
- [ ] 3+ working agents
- [ ] ASI:One correctly routes 80%+ of intents

### Phase 3 Success Criteria
- [ ] Desktop integration working on all platforms (Win/Mac/Linux)
- [ ] 5+ external API integrations
- [ ] End-to-end latency <10s for simple tasks

### Phase 4 Success Criteria
- [ ] Multi-agent workflows executing successfully
- [ ] Proactive actions accepted by user >50% of time
- [ ] User reports feeling "never alone" :)

---

## 🚀 Getting Started - Next Actions

### Immediate Steps (This Week)

1. **Set up Event Queue**
   ```bash
   # Create Pub/Sub topic
   gcloud pubsub topics create omi-events --project calhacks-omi-audio
   gcloud pubsub subscriptions create omi-events-sub --topic omi-events
   ```

2. **Create Fetch.ai Accounts**
   - Sign up at https://as1.ai (ASI:One)
   - Create Agentverse account
   - Get API keys

3. **Build Agent Orchestrator Service**
   ```bash
   mkdir universal-context/agent-orchestrator
   cd universal-context/agent-orchestrator
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install flask google-cloud-pubsub requests uagents
   ```

4. **Develop First Agent**
   - Start with Task Classification Agent
   - Use existing transcriptions to test
   - Register in Agentverse

5. **Test End-to-End Flow**
   - Record audio → transcribe → classify → log result
   - Validate each step works

---

## 📚 Key Resources

### Documentation
- [Omi API Docs](https://docs.omi.me)
- [Fetch.ai uAgents](https://fetch.ai/docs/examples/uagents)
- [ASI:One Documentation](https://docs.asi1.ai)
- [Agentverse Docs](https://docs.agentverse.ai)
- [Supermemory API](https://supermemory.ai/docs)

### Code Repositories
- Current project: `D:\Projects\never-be-alone`
- Fetch.ai uAgents: https://github.com/fetchai/uAgents
- Omi SDK: https://github.com/BasedHardware/omi

### Community
- Fetch.ai Discord: https://discord.gg/fetchai
- Omi Discord: https://discord.gg/omi
- Supermemory Discord: https://discord.gg/supermemory

---

## 🎨 Alternative Architectures Considered

### Option A: Claude as Orchestrator (Simpler)
Instead of Fetch.ai, use Claude via MCP:
- Pros: Already integrated, familiar, simpler
- Cons: Less specialized for agent routing, no agent marketplace
- **Decision**: Good for MVP/testing, but Fetch.ai better for production scale

### Option B: LangGraph for Orchestration
Use LangChain's LangGraph for multi-agent workflows:
- Pros: Python-native, lots of examples, flexible
- Cons: Self-hosted orchestration logic, no discovery layer
- **Decision**: Could be used alongside Fetch.ai for complex workflows

### Option C: Custom Orchestrator
Build from scratch:
- Pros: Full control, customized for use case
- Cons: Reinventing the wheel, maintenance burden
- **Decision**: Not recommended, use existing platforms

---

## ✅ Decision: Fetch.ai ASI:One + Agentverse

**Why Fetch.ai?**
1. **Purpose-built for agent orchestration** - not a general LLM
2. **Agent marketplace** - can leverage community agents
3. **Standardized Chat Protocol** - interoperability
4. **Routing layer** - ASI:One handles intent classification
5. **Scalability** - designed for multi-agent systems
6. **Active development** - recent launches, growing ecosystem

**Integration Points**:
- Event queue → ASI:One (intent routing)
- Agentverse → Specialized agents (task execution)
- Agents → External APIs (Gmail, Calendar, etc.)
- Agents → Desktop MCP server (local actions)
- Agents → Supermemory (context storage)

---

## 🔮 Future Vision (Phase 5+)

1. **Vision Support**
   - Analyze images from Omi Glass
   - "What am I looking at?"
   - Visual memory search

2. **Voice Output**
   - Agents respond via audio
   - TTS integration
   - Conversational interface

3. **Mobile App**
   - View agent activity on phone
   - Push notifications
   - Manual agent invocation

4. **Agent Marketplace**
   - Users create custom agents
   - Share with community
   - Monetization for agent developers

5. **Multi-User Context**
   - Shared memories between users
   - Family/team contexts
   - Collaborative agents

---

**This is a living document. Update as implementation progresses!**

Last Updated: 2025-10-25
Version: 1.0
Author: Never Be Alone Team
