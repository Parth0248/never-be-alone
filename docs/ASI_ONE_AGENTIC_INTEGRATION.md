# ASI:One Agentic Integration Guide

## Overview

The Never-Be-Alone project now features a sophisticated **ASI:One Agentic Layer** that handles complex, multi-step tasks requiring agent orchestration from the Agentverse marketplace. This layer sits atop the existing architecture and provides intelligent task routing based on complexity analysis.

---

## Architecture

### Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                Layer 1: Hardware (Omi DevKit 2 / Glass)         │
│                  Audio Transcription + Images                   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│         Layer 2: Universal Context (Supermemory)                │
│         - Retrieve relevant memories & past context             │
│         - Store all interactions & outputs                      │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│       Layer 3: Multimodal Understanding (Reka.ai)               │
│       - Process images + transcripts + memories                 │
│       - Generate enhanced understanding & entities              │
│       - Create contextually-aware prompts                       │
└────────────┬────────────────────────────────────────────────────┘
             │
             │  Complexity Analysis
             │
             ├─────────► SIMPLE TASK (complexity 1-5)
             │           - Direct agent execution
             │           - Quick Omi response
             │           └──► Store in Supermemory
             │
             └─────────► COMPLEX TASK (complexity 6-10)
                         │
                         ▼
        ┌────────────────────────────────────────────────┐
        │  Layer 4: ASI:One Agentic Orchestration        │
        │  - Dynamic model selection                     │
        │  - Multimodal input (images + text)            │
        │  - Agentverse marketplace discovery            │
        │  - Multi-agent coordination                    │
        │  - Async polling for long tasks                │
        └────────────┬───────────────────────────────────┘
                     │
                     ├──► Send to user (Omi Client)
                     └──► Store in Supermemory
```

---

## Key Features

### 1. **Dynamic Model Selection**

ASI:One offers three agentic models. The system automatically selects the appropriate one based on task complexity:

| Complexity Score | Model Used               | Context Window | Use Case                           |
| ---------------- | ------------------------ | -------------- | ---------------------------------- |
| 1-3              | `asi1-fast-agentic`      | 24K tokens     | Simple queries, observations       |
| 4-7              | `asi1-agentic`           | 32K tokens     | Moderate tasks, single reminders   |
| 8-10             | `asi1-extended-agentic`  | 64K tokens     | Complex multi-agent workflows      |

**Complexity Factors:**
- Intent type (scheduling > reminder > search > observation)
- Number of entities detected
- Text length (word count)
- Temporal complexity (multiple time references)
- Multi-step indicators ("then", "after", "and then")

### 2. **Multimodal Support**

The agentic client accepts both images and text:
- Images from Omi Glass (via Reka processing)
- Enhanced understanding from Reka's vision analysis
- Contextually-aware prompts combining visual and textual information

### 3. **Intelligent Task Routing**

**Simple Tasks** (handled locally):
- "What's the weather today?"
- "Tell me about my last conversation"
- "What did I talk about with John?"

**Complex Tasks** (routed to ASI:One Agentic):
- "Remind me tomorrow at 2pm to call mom AND send her an email tonight"
- "Schedule a meeting with design team next Tuesday and book conference room"
- "I have 3 hours at the airport, find a restaurant and book it"
- "When I get home, remind me to review the presentation I saw today"

### 4. **Async Agent Execution**

For tasks requiring Agentverse agents that take time to execute:
- ASI:One returns a deferred response
- System polls every 5 seconds for up to 2 minutes
- User receives final result once agents complete

### 5. **Dual Output Routing**

All responses are:
1. **Sent to user** via Omi Client API
2. **Stored in Supermemory** for future context retrieval

---

## Setup

### Prerequisites

Ensure you have the following in your `.env` file:

```bash
# ASI:One Configuration
ASI_ONE_API_KEY=sk_your_api_key_here

# Omi App Configuration
OMI_API_KEY=sk_your_omi_key_here
OMI_APP_ID=your_app_id_here
OMI_USER_ID=your_user_id_here

# Reka.ai Configuration
REKA_API_KEY=your_reka_key_here
REKA_MODEL=reka-flash

# Supermemory Configuration
SUPERMEMORY_API_KEY=sm_your_key_here
SUPERMEMORY_BASE_URL=https://api.supermemory.ai/
```

### Installation

```bash
cd agent-orchestrator
pip install -r requirements.txt
```

---

## Usage

### Running the Orchestrator

```bash
cd agent-orchestrator
python omi_webhook_integration.py
```

This starts the webhook server that receives transcriptions from Omi devices and processes them through the complete pipeline.

### Testing the Integration

Run the comprehensive test suite:

```bash
cd agent-orchestrator
python test_asi_one_agentic.py
```

**Test Coverage:**
1. Simple query routing (should NOT use agentic)
2. Complex reminder (should use agentic)
3. Direct agentic client call
4. Complexity scoring system
5. Multimodal support (images + text)

### Manual Testing

```python
import asyncio
from orchestrator import get_orchestrator

async def test():
    orchestrator = get_orchestrator()

    result = await orchestrator.process_transcription(
        transcription="Remind me tomorrow at 2pm to call the dentist",
        context={
            "uid": "user_123",
            "timestamp": "2025-10-26T10:00:00Z"
        }
    )

    print(result)

asyncio.run(test())
```

---

## Code Structure

### New Files

1. **`asi_one_agentic_client.py`**
   - Enhanced ASI:One client with multimodal support
   - Dynamic model selection
   - Complexity calculation
   - Async polling support

2. **`test_asi_one_agentic.py`**
   - Comprehensive test suite
   - 5 test scenarios covering all features

### Modified Files

1. **`orchestrator.py`**
   - Added ASI:One agentic client
   - Implemented complexity-based routing
   - Integrated Omi client for output
   - Enhanced Supermemory storage with agentic responses

2. **`omi_client.py`** (copied to agent-orchestrator)
   - Used for sending responses to users

---

## Demo Scenarios for Sponsors

### 1. Groq (Transcription)
**Demo:** "Real-time Multi-language Meeting Assistant"

```
User: "Let's schedule a follow-up meeting next Tuesday at 2pm with the design team"
↓ Groq transcribes
↓ ASI:One discovers calendar agent from Agentverse
↓ Creates event + sends invite
→ Response delivered via Omi + stored in Supermemory
```

### 2. Supermemory (Memory)
**Demo:** "Context-Aware Proactive Reminders"

```
User mentions: "I need to call mom tomorrow about her birthday gift"
↓ Supermemory stores with mom's preferences from past
↓ Next day: ASI:One retrieves context + sends reminder with gift suggestions
→ Proactive, contextual assistance
```

### 3. Fetch.ai (AI Agents)
**Demo:** "Multi-Agent Travel Planning"

```
User at airport (via Omi Glass): "I have 3 hours, find me a restaurant and book it"
↓ Reka processes Glass images (sees airport terminal)
↓ ASI:One discovers: location agent + restaurant agent + booking agent
↓ Orchestrates: Find location → Search → Check availability → Book
→ Confirmation sent to user
```


### 4. Omi/Based Hardware (Hardware Sponsor)
**Demo:** "Vision-Driven Smart Home Control"

```
Omi Glass captures: User looking at messy desk
↓ Reka: "User viewing cluttered workspace with documents"
↓ ASI:One discovers: task management + calendar agents
↓ Creates tasks from visible papers + schedules cleanup
→ Sent to phone via Omi
```

### 5. Anthropic/MCP (MCP Automation Sponsor)
**Demo:** "MCP-Powered Workflow Automation"

```
User: "When I get home, remind me to review the presentation I saw today"
↓ ASI:One uses MCP tools via Supermemory
↓ Geofenced reminder + retrieves presentation images from Glass
→ Smart, location-aware automation
```

---

## API Reference

### ASIOneAgenticClient

#### `process_complex_task()`

```python
def process_complex_task(
    text: str,
    images_base64: Optional[List[str]] = None,
    entities: Optional[Dict[str, Any]] = None,
    intent: Optional[str] = None,
    reka_understanding: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    conversation_id: Optional[str] = None,
    stream: bool = False
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "success": True,
    "response": "Agent response text",
    "agents_used": ["agent1", "agent2"],
    "model_used": "asi1-agentic",
    "complexity_score": 7,
    "session_id": "uuid",
    "requires_polling": False
}
```

#### `calculate_complexity()`

```python
def calculate_complexity(
    text: str,
    entities: Dict[str, Any],
    intent: str,
    reka_understanding: Optional[Dict[str, Any]] = None
) -> int
```

Returns complexity score (1-10) based on task analysis.

#### `select_model()`

```python
def select_model(
    complexity_score: int,
    multi_agent: bool = False
) -> ModelType
```

Returns appropriate ASI:One model based on complexity.

---

## Troubleshooting

### Issue: "ASI:One API error"

**Solution:** Check your API key in `.env`:
```bash
ASI_ONE_API_KEY=sk_your_key_here
```

### Issue: "OMI_USER_ID not configured"

**Solution:** Add your Omi user ID to `.env`:
```bash
OMI_USER_ID=your_user_id_here
```

### Issue: Complex tasks not routed to agentic

**Solution:** Check complexity calculation. Add debug logging:
```python
complexity = self.asi_one_agentic.calculate_complexity(text, entities, intent)
print(f"Complexity: {complexity}/10")
```

### Issue: Async polling timeout

**Solution:** Increase polling attempts in `orchestrator.py`:
```python
final_response = self.asi_one_agentic.poll_for_agent_result(
    conversation_id=conv_id,
    max_attempts=48,  # Increase from 24
    wait_seconds=5
)
```

---

## Performance Considerations

### Model Selection Impact

- **asi1-fast-agentic**: ~2-3s response time
- **asi1-agentic**: ~3-5s response time
- **asi1-extended-agentic**: ~5-10s response time

### Async Operations

Long-running Agentverse agents can take up to 2 minutes. The system:
1. Returns immediately with deferred status
2. Polls every 5 seconds
3. Sends final result to user when ready

### Caching

- Session IDs are cached per conversation
- Supermemory provides context caching
- Reka results are passed to ASI:One to avoid re-processing

---

## Future Enhancements

1. **Streaming Support**: Real-time token streaming from ASI:One
2. **Multi-Turn Conversations**: Maintain session state across multiple interactions
3. **Agent Marketplace Integration**: Direct browsing of Agentverse agents
4. **Custom Agent Creation**: Define project-specific agents
5. **Performance Analytics**: Track complexity scores and model selection accuracy

---

## Questions & Answers

### Q1: Can we dynamically allocate ASI:One model versions?

**A:** Yes! The system automatically selects models based on complexity:
- Complexity 1-3 → `asi1-fast-agentic`
- Complexity 4-7 → `asi1-agentic`
- Complexity 8-10 → `asi1-extended-agentic`

### Q2: Can we input both images and text to ASI:One?

**A:** Yes! The client supports multimodal input:
```python
agentic_result = client.process_complex_task(
    text="What do you see here?",
    images_base64=[base64_image],
    reka_understanding=reka_context
)
```

### Q3: How are outputs shared with the user?

**A:** All responses are:
1. Sent to user via `omi_client.send_response()`
2. Stored in Supermemory via `context_agent.store_memory()`

---

## Contributing

To extend the ASI:One agentic integration:

1. **Add new complexity factors** in `calculate_complexity()`
2. **Define new intents** in `is_complex_task()`
3. **Add custom agents** in the orchestrator
4. **Extend test coverage** in `test_asi_one_agentic.py`

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/Parth0248/never-be-alone/issues
- Documentation: This file

---

**Built with ❤️ at Cal Hacks 2025**
