# Integration Options Comparison
## How to Access and Control: Omi, Desktop, and Beyond

---

## 🤔 The Question

You asked: **"Can we interact with Omi from external API? And how do we integrate with desktop (Claude or something else)?"**

This document compares all integration pathways and recommends the best approach.

---

## 📱 Option 1: Omi Wearable Integration

### A. Webhook-Based (Current - RECOMMENDED ✅)

**How it works:**
```
Omi Device → Webhook Server (Cloud) → Agent Orchestrator
```

**Capabilities:**
- ✅ **Audio streaming**: Real-time PCM audio every 5-10s
- ✅ **Transcriptions**: Pre-transcribed text from Omi app
- ✅ **Bidirectional**: Can send responses back via Omi API
- ✅ **Always on**: Works even when phone is locked

**Implementation:**
```python
# Already working in your project!
@app.route('/audio', methods=['POST'])
def handle_audio():
    # Receives raw PCM audio from Omi
    audio_data = request.get_data()
    # Process and trigger agents
```

**Pros:**
- Already implemented and working
- No phone dependency after setup
- Cloud-hosted, scales easily
- Device agnostic (works with DevKit 2 & Glass)

**Cons:**
- Requires internet connectivity
- Webhook endpoint must be public
- Need to manage cloud infrastructure

**Cost:** ~$10-20/month (Cloud Run + GCS + transcription)

---

### B. Omi App Plugin/External API (LIMITED 🟡)

**Research Findings:**
From Omi documentation, there are two integration methods:

1. **App Plugins**
   - Build custom plugins for Omi mobile app
   - Written in Dart/Flutter
   - Runs on user's phone
   - Limited to what mobile app exposes

2. **External API** (No public documentation found)
   - Omi doesn't currently expose a REST API for external access
   - Can't directly query device status or pull data
   - **Webhook is the main integration method**

**Recommendation:** Stick with webhook-based approach. Omi is designed for **push** (device sends data) not **pull** (external queries).

---

## 💻 Option 2: Desktop Integration

### A. Claude MCP Server (BEST for Claude Integration ✅)

**How it works:**
```
Fetch.ai Agent → Local MCP Server → Claude Desktop
                                  ↓
                          Supermemory MCP (already working)
```

**What is MCP?**
- Model Context Protocol by Anthropic
- Allows Claude to access local tools and data
- You already have Supermemory MCP configured!

**Implementation:**

1. **Create Custom MCP Server for Agent Actions**

```python
# desktop-integration/mcp-agent-bridge/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio

# Initialize MCP server
app = Server("never-be-alone")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="trigger_agent_action",
            description="Trigger an action from Fetch.ai agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_type": {
                        "type": "string",
                        "enum": ["calendar", "email", "search", "reminder"],
                        "description": "Which agent to invoke"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Action parameters"
                    }
                },
                "required": ["agent_type", "action"]
            }
        ),
        types.Tool(
            name="desktop_notification",
            description="Show desktop notification from agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "message": {"type": "string"},
                    "urgency": {"type": "string", "enum": ["low", "normal", "critical"]}
                },
                "required": ["title", "message"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "trigger_agent_action":
        # Forward to Fetch.ai agent orchestrator
        result = await trigger_agent(
            agent_type=arguments["agent_type"],
            action=arguments["action"],
            parameters=arguments.get("parameters", {})
        )
        return [types.TextContent(type="text", text=str(result))]

    elif name == "desktop_notification":
        show_notification(arguments["title"], arguments["message"])
        return [types.TextContent(type="text", text="Notification shown")]

async def trigger_agent(agent_type, action, parameters):
    """Call Fetch.ai agent via API"""
    import requests
    response = requests.post(
        "http://localhost:8080/trigger-agent",
        json={
            "agent_type": agent_type,
            "action": action,
            "parameters": parameters
        }
    )
    return response.json()

def show_notification(title, message):
    """Show desktop notification"""
    import platform
    if platform.system() == 'Windows':
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=10)
    elif platform.system() == 'Darwin':
        import os
        os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
    elif platform.system() == 'Linux':
        import os
        os.system(f'notify-send "{title}" "{message}"')

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(app))
```

2. **Configure in Claude Desktop**

```json
// claude_desktop_config.json (Windows: %APPDATA%/Claude/claude_desktop_config.json)
{
  "mcpServers": {
    "supermemory": {
      "command": "npx",
      "args": ["-y", "@supermemory/mcp-server"]
    },
    "never-be-alone": {
      "command": "python",
      "args": ["D:/Projects/never-be-alone/desktop-integration/mcp-agent-bridge/server.py"],
      "env": {
        "AGENT_API_URL": "http://localhost:8080"
      }
    }
  }
}
```

3. **Usage in Claude**

```
User: "Show me what I said about the book recommendation last week"
Claude: [Uses Supermemory MCP to search] → "You mentioned 'Atomic Habits'..."

User: "Create a reminder to buy that book tomorrow"
Claude: [Uses never-be-alone MCP] → "Triggered calendar agent to create reminder"
```

**Pros:**
- Native Claude integration
- Access to Supermemory + Agent actions
- Secure (runs locally)
- No additional authentication needed

**Cons:**
- Requires Claude Desktop running
- Limited to actions available in MCP tools
- Can't proactively notify user (agent → Claude)

**Cost:** Free (runs locally)

---

### B. Local API Server + Desktop Agent (Most Flexible 🌟)

**How it works:**
```
Fetch.ai Agent (Cloud) ←→ Desktop API Server (Local) ←→ Desktop Actions
                            ↓
                     WebSocket/ngrok tunnel
```

**Implementation:**

```python
# desktop-integration/desktop-server/main.py
from flask import Flask, request, jsonify
import pyautogui
import subprocess
import webbrowser
import json
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Authentication token (generate and share with cloud agent)
API_TOKEN = "your-secure-token-here"

def require_auth(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token != API_TOKEN:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/execute', methods=['POST'])
@require_auth
def execute_action():
    """Execute desktop action from cloud agent"""
    data = request.get_json()
    action_type = data.get('action_type')

    try:
        if action_type == 'notification':
            show_notification(data['title'], data['message'])
            return jsonify({'success': True})

        elif action_type == 'open_url':
            webbrowser.open(data['url'])
            return jsonify({'success': True, 'url': data['url']})

        elif action_type == 'open_app':
            subprocess.Popen(data['app_path'])
            return jsonify({'success': True})

        elif action_type == 'clipboard':
            import pyperclip
            pyperclip.copy(data['text'])
            return jsonify({'success': True})

        elif action_type == 'type_text':
            pyautogui.write(data['text'])
            return jsonify({'success': True})

        elif action_type == 'run_script':
            result = subprocess.run(
                data['script'],
                shell=True,
                capture_output=True,
                text=True
            )
            return jsonify({
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr
            })

        else:
            return jsonify({'error': 'Unknown action type'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle agent connection"""
    print('Agent connected')
    emit('connection_status', {'status': 'connected'})

@socketio.on('agent_action')
def handle_agent_action(data):
    """Receive real-time actions from agents"""
    print(f'Agent action: {data}')
    execute_action_from_socket(data)

def show_notification(title, message):
    # Same as before
    pass

if __name__ == '__main__':
    port = 5555
    print(f'Desktop API server running on http://localhost:{port}')
    socketio.run(app, host='0.0.0.0', port=port)
```

**Expose to Cloud via ngrok:**

```bash
# Install ngrok
# Download from https://ngrok.com/download

# Start tunnel
ngrok http 5555

# Outputs: https://abc123.ngrok.io → http://localhost:5555

# Save this URL in your agent orchestrator
export DESKTOP_API_URL=https://abc123.ngrok.io
```

**Agent Uses Desktop API:**

```python
# In your Fetch.ai agent
import requests

async def send_desktop_notification(uid, title, message):
    """Send notification to user's desktop"""
    desktop_url = get_user_desktop_url(uid)  # Stored in DB

    response = requests.post(
        f"{desktop_url}/execute",
        headers={'Authorization': f'Bearer {get_user_token(uid)}'},
        json={
            'action_type': 'notification',
            'title': title,
            'message': message
        }
    )

    return response.json()
```

**Pros:**
- Full desktop control (keyboard, mouse, apps)
- Bi-directional: Agent can push notifications
- Works with any desktop app
- Very flexible (run scripts, open apps, etc.)

**Cons:**
- Security risk if not properly secured
- Requires ngrok or port forwarding
- Must run continuously on desktop

**Cost:** Free (ngrok free tier sufficient)

---

### C. Electron App (Most Polished 🎨)

Build a dedicated desktop app:

```javascript
// electron-app/main.js
const { app, BrowserWindow, ipcMain, Notification } = require('electron')
const io = require('socket.io-client')

// Connect to agent orchestrator
const socket = io('wss://your-agent-orchestrator.com')

socket.on('agent-action', (data) => {
  if (data.action === 'notification') {
    new Notification({
      title: data.title,
      body: data.message
    }).show()
  }
})

// IPC for renderer process
ipcMain.handle('trigger-agent', async (event, agentType, action, params) => {
  // Send to Fetch.ai agents
  const response = await fetch('https://your-orchestrator.com/trigger', {
    method: 'POST',
    body: JSON.stringify({ agentType, action, params })
  })
  return response.json()
})
```

**Pros:**
- Professional UI
- Cross-platform (Win/Mac/Linux)
- Can show agent activity dashboard
- Auto-update functionality

**Cons:**
- More complex to build
- Distribution/installation required
- Overkill for MVP

**Cost:** Free (build yourself) or paid (hire developer)

---

## 🔄 Option 3: Hybrid Multi-Channel Integration (RECOMMENDED 🏆)

### The Best Approach: Combine All Three

```
                    ┌─────────────────────────────────┐
                    │   Fetch.ai Agent Orchestrator   │
                    │         (Cloud - Always On)      │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
         ┌──────────▼─────────┐    ┌─────────▼──────────┐
         │  Omi Wearable      │    │  Desktop (when on) │
         │  (Always Listening)│    │                    │
         │                    │    │  ┌──────────────┐  │
         │  • Audio capture   │    │  │ Claude MCP   │  │
         │  • Transcriptions  │    │  │ (Supermemory)│  │
         │  • Context gathering   │    │  └──────────────┘  │
         └────────────────────┘    │                    │
                                   │  ┌──────────────┐  │
                                   │  │ Desktop API  │  │
                                   │  │ (Actions)    │  │
                                   │  └──────────────┘  │
                                   └────────────────────┘
```

**Scenario 1: User wearing Omi, at desk**
1. Omi captures: "Remind me to review the Johnson proposal tomorrow"
2. Agent creates reminder in Google Calendar
3. Desktop notification pops up: "Reminder created for tomorrow"
4. Claude shows in MCP: "Recent action: Calendar event created"

**Scenario 2: User wearing Omi, away from desk**
1. Omi captures: "Send email to Sarah about meeting"
2. Agent drafts email using context from Supermemory
3. Sends via Gmail API
4. Stores in Supermemory: "Email sent to Sarah re: meeting"
5. When user returns to desk, Claude can show: "You sent an email to Sarah at 2:30pm"

**Scenario 3: User at desk, no Omi**
1. User asks Claude: "What did I talk about with John yesterday?"
2. Claude uses Supermemory MCP → Retrieves conversation
3. User: "Send him a follow-up email about the AI project"
4. Claude uses never-be-alone MCP → Triggers email agent
5. Agent drafts and sends email

---

## 📊 Integration Comparison Matrix

| Feature | Omi Webhook | Claude MCP | Desktop API | Electron App |
|---------|-------------|------------|-------------|--------------|
| **Always On** | ✅ | ❌ (needs Claude open) | ❌ (needs server running) | ⚠️ (needs app running) |
| **Bidirectional** | ⚠️ (mostly push) | ✅ | ✅ | ✅ |
| **Desktop Control** | ❌ | ⚠️ (limited) | ✅ | ✅ |
| **Omi Integration** | ✅ | ❌ | ❌ | ⚠️ (via webhook) |
| **Security** | ✅ (cloud-hosted) | ✅ (local) | ⚠️ (needs ngrok) | ✅ (local) |
| **Setup Complexity** | ⭐⭐ (medium) | ⭐ (easy) | ⭐⭐ (medium) | ⭐⭐⭐ (complex) |
| **Cost** | $10-20/mo | Free | Free | Free (DIY) |
| **Scalability** | ✅ | ❌ | ❌ | ❌ |
| **User Experience** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Recommended Implementation Strategy

### Phase 1 (Current): Omi Webhook + Cloud Agents ✅
- ✅ Already have webhook receiving audio
- ✅ GCS storage working
- 🚧 Add agent orchestration with Fetch.ai
- 🚧 Add Groq transcription automation

### Phase 2: Claude MCP Integration
- Build custom MCP server for agent actions
- Allow Claude to trigger agents
- Show agent activity in Claude
- **Timeline:** 1 week

### Phase 3: Desktop API (Optional)
- For users who want desktop control
- Build if there's demand for notifications
- **Timeline:** 1-2 weeks

### Phase 4: Electron App (Future)
- Build if product gains traction
- Create polished UI for agent dashboard
- **Timeline:** 1-2 months

---

## 🔧 Quick Start: Add Claude MCP Today

You can add basic Claude integration **right now** with minimal code:

```python
# desktop-integration/simple-mcp-server.py
import sys
import json

def handle_request(request):
    """Handle MCP request from Claude"""
    method = request.get('method')

    if method == 'tools/list':
        return {
            'tools': [
                {
                    'name': 'show_agent_status',
                    'description': 'Show status of running agents',
                    'inputSchema': {'type': 'object', 'properties': {}}
                }
            ]
        }

    elif method == 'tools/call':
        tool_name = request.get('params', {}).get('name')
        if tool_name == 'show_agent_status':
            # Query agent orchestrator
            import requests
            status = requests.get('http://localhost:8080/agent-status').json()
            return {'content': [{'type': 'text', 'text': str(status)}]}

# MCP stdio protocol
for line in sys.stdin:
    request = json.loads(line)
    response = handle_request(request)
    print(json.dumps(response))
    sys.stdout.flush()
```

Add to Claude config:

```json
{
  "mcpServers": {
    "never-be-alone": {
      "command": "python",
      "args": ["D:/Projects/never-be-alone/desktop-integration/simple-mcp-server.py"]
    }
  }
}
```

**Test in Claude:**
```
User: "Show me the status of my agents"
Claude: [Uses show_agent_status tool] → "Task Classifier: Active, Calendar Agent: Active, ..."
```

---

## 🎉 Conclusion & Next Steps

### Answer to Your Question:

1. **"Can we interact with Omi from external API?"**
   - **Answer:** Not directly via API (not documented). Use **webhook method** (which you've already implemented!). This is the recommended approach.

2. **"How to integrate with desktop (Claude or something else)?"**
   - **Answer:**
     - **For Claude:** Build MCP server (easiest, 1 day of work)
     - **For full desktop control:** Build desktop API with ngrok (medium, 3-5 days)
     - **For polished experience:** Build Electron app (complex, weeks)

### Immediate Action Items:

1. ✅ **Keep using Omi webhooks** - working great!
2. 🚧 **Implement agent orchestration** - follow QUICK_START guide
3. 🆕 **Build simple MCP server** - integrate with Claude (1 day)
4. 🔮 **Consider desktop API** - if you need notifications (optional)

---

**You have all the pieces! The architecture is solid. Start with agent orchestration, then add Claude MCP. Ship it! 🚀**
