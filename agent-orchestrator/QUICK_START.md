## Quick Start Guide - Agent Orchestration System

Get the agent orchestration layer running in 5 minutes!

### Prerequisites

- Python 3.8 or higher
- API Keys (already configured in `.env`):
  - ASI:One API Key ✓
  - Agentverse API Key ✓
  - Supermemory API Key ✓
  - Groq API Key ✓

### Installation

The project uses a shared virtual environment at the root level (`../.venv`).

#### Windows
```bash
# From project root
.venv\Scripts\activate
cd agent-orchestrator
pip install -r requirements.txt
```

#### Mac/Linux
```bash
# From project root
source .venv/bin/activate
cd agent-orchestrator
pip install -r requirements.txt
```

### Quick Test

#### 1. Check Agent Status
```bash
python test_orchestrator.py status
```

This shows all available agents and their capabilities.

#### 2. Test a Simple Transcription
```bash
python test_orchestrator.py text "Remind me to call mom tomorrow at 3pm"
```

This processes a transcription through the full orchestration pipeline.

#### 3. Test Multiple Scenarios
```bash
python test_orchestrator.py all
```

Runs through 8 different test scenarios to verify all agent types.

### Start the Server

```bash
python main.py
```

Server will start on `http://localhost:8080`

### API Usage

#### Process a Transcription

```bash
curl -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "transcription": "Remind me to call mom tomorrow at 3pm",
    "context": {
      "uid": "user123",
      "timestamp": "2025-10-25T14:30:00Z"
    }
  }'
```

#### List Available Agents

```bash
curl http://localhost:8080/agents
```

#### Test Specific Agent

```bash
curl -X POST http://localhost:8080/test-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "calendar_agent",
    "action": "create_reminder",
    "params": {
      "text": "Call mom",
      "time": "tomorrow"
    }
  }'
```

### Example Transcriptions to Test

Try these with `python test_orchestrator.py text "<transcription>"`:

1. **Reminders**: "Remind me to call mom tomorrow at 3pm"
2. **Questions**: "What did I say about the meeting last week?"
3. **Smart Home**: "Turn on the living room lights"
4. **Communication**: "Send an email to John about the project"
5. **Scheduling**: "Schedule a team meeting for next Monday at 10am"
6. **Observations**: "I'm feeling happy today"

### Available Agents

#### 1. Task Classification Agent
- Analyzes transcriptions
- Extracts intent and entities
- Categorizes requests
- Determines urgency

**Actions**: `classify`, `extract_entities`, `categorize`

#### 2. Calendar & Reminder Agent
- Creates reminders
- Schedules events
- Parses natural language time references
- Lists and manages reminders

**Actions**: `create_reminder`, `create_event`, `list_reminders`, `delete_reminder`

#### 3. Context Retrieval Agent
- Searches Supermemory
- Answers questions using past context
- Stores new memories
- Retrieves relevant information

**Actions**: `search`, `get_context`, `answer_question`, `store_memory`

### Architecture Flow

```
Transcription
    ↓
ASI:One (Intent Analysis)
    ↓
Agent Routing
    ↓
Specialized Agents Execute
    ↓
Store in Supermemory
    ↓
Return Results
```

### Discovering Agentverse Agents

Find additional community agents for enhanced functionality:

```bash
# Show recommended agent types
python agentverse_integration.py recommend

# Discover available agents
python agentverse_integration.py discover

# Search for specific task agents
python agentverse_integration.py search "time tracking"
```

### Integration with Omi Transcription Pipeline

To connect this to your existing Omi webhook server:

#### Option 1: Direct API Call (Recommended for Local Testing)

In your webhook server (`universal-context/webhook-server/src/index.ts`), add after transcription:

```typescript
// After storing transcription in GCS
const orchestratorUrl = 'http://localhost:8080/orchestrate';

await fetch(orchestratorUrl, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    transcription: transcriptionText,
    context: {
      uid: uid,
      timestamp: new Date().toISOString(),
      source: 'omi_device'
    }
  })
});
```

#### Option 2: Event Queue (Production)

Set up Google Cloud Pub/Sub:

```bash
# Create topic
gcloud pubsub topics create omi-transcriptions

# Agent orchestrator subscribes to this topic
# See AGENT_ORCHESTRATION_ARCHITECTURE.md for details
```

### Troubleshooting

#### API Key Issues
- Check `.env` file has all keys filled in
- Verify ASI:One key is valid: `curl https://api.asi1.ai/v1/status -H "Authorization: Bearer <key>"`

#### Import Errors
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

#### Agent Not Found
- Check agent is registered in `orchestrator.py`
- Verify agent class is imported in `agents/__init__.py`

### Next Steps

1. **Test End-to-End**: Process real Omi transcriptions through the system
2. **Add More Agents**: Create custom agents for specific use cases
3. **Integrate Agentverse**: Add community agents for expanded functionality
4. **Deploy**: Move from localhost to cloud hosting
5. **Monitor**: Set up logging and monitoring for production use

### Development

#### Add a New Agent

1. Create agent file in `agents/`:

```python
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent", "Description")

    async def handle_task(self, action, params):
        # Your logic here
        pass

    def get_capabilities(self):
        return {...}
```

2. Register in `agents/__init__.py`:

```python
from .my_agent import MyAgent
__all__ = [..., 'MyAgent']
```

3. Add to orchestrator in `orchestrator.py`:

```python
self.agents = {
    ...
    "my_agent": MyAgent()
}
```

#### Run Tests
```bash
pytest tests/  # When test suite is created
```

### Resources

- [ASI:One Documentation](https://docs.asi1.ai)
- [Agentverse Docs](https://docs.agentverse.ai)
- [Fetch.ai uAgents](https://fetch.ai/docs/examples/uagents)
- [Supermemory API](https://supermemory.ai/docs)

### Support

For issues or questions:
- Check logs in console output
- Review `AGENT_ORCHESTRATION_ARCHITECTURE.md` for detailed architecture
- Test individual agents with `test_orchestrator.py`

---

**You're all set!** 🚀 Start with `python test_orchestrator.py status` to verify everything is working.
