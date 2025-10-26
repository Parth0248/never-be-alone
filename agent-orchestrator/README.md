# Agent Orchestration Layer - Never Be Alone

AI agent orchestration system using Fetch.ai ASI:One and Agentverse to transform passive context capture into intelligent actions.

## Architecture

```
Transcription → ASI:One Orchestrator → Specialized Agents → Actions
```

### Components

1. **ASI:One Orchestrator**: Main routing layer that analyzes transcriptions and delegates to specialized agents
2. **Specialized Agents**:
   - Task Classification Agent
   - Calendar & Reminder Agent
   - Context Retrieval Agent
   - Communication Agent
   - Smart Home Agent
3. **Agentverse Integration**: Discover and use community agents

## Setup

### 1. Install Dependencies

```bash
cd agent-orchestrator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

### 3. Run the Orchestrator

```bash
python main.py
```

## Usage

### Test with a Sample Transcription

```bash
python test_orchestrator.py --text "Remind me to call mom tomorrow at 3pm"
```

### Connect to Transcription Pipeline

The orchestrator listens for transcription events and automatically routes them to appropriate agents.

## Agent Development

Create custom agents in the `agents/` directory. See `agents/task_classifier.py` for an example.

## API Endpoints

- `POST /orchestrate` - Send transcription for agent routing
- `GET /agents` - List registered agents
- `GET /health` - Health check

## Testing

```bash
pytest tests/
```

## Architecture Diagram

See `AGENT_ORCHESTRATION_ARCHITECTURE.md` in the root directory for detailed architecture.
