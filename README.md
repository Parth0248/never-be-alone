# Never Be Alone 🎧

> **An Intelligent Multimodal AI Companion System**

Streamline interaction between Humans and AI in both digital and physical world with Open Source Wearable AI devices.

Built at **Cal Hacks 2025** - October 25-26, 2025

## Overview

Never Be Alone is a comprehensive AI-powered companion system that integrates with Omi wearable devices (DevKit 2 and Glass) to provide seamless audio transcription, universal memory storage, and intelligent agentic interactions.

## Features

- **Real-time Audio Processing**: Receive and process audio streams from Omi wearables every 5 seconds
- **AI Transcription**: High-quality speech-to-text using Groq Whisper-large-v3
- **Universal Memory**: Store all conversations and context in Supermemory for persistent access
- **Dual Webhook Support**: Handle both raw audio bytes and pre-transcribed text
- **Agentic Layer**: Fetch.ai ASI:One integration for intelligent AI agents (coming soon)
- **Vision Processing**: Support for Omi Glass with vision capabilities (coming soon)
- **Custom MCP Server**: Model Context Protocol automation (in development)

## Technical Stack

- **Webhook Infrastructure**: Cloudflare Workers (serverless, globally distributed)
- **Transcription**: Groq Whisper-large-v3 (state-of-the-art speech-to-text)
- **Storage**: Supermemory API (universal memory and context management)
- **Agentic Layer**: Fetch.ai ASI:One (intelligent AI agents)
- **Hardware**: Omi DevKit 2 & Omi Glass (open-source wearables)
- **Temporary Storage**: Cloudflare KV (audio chunks and transcriptions)

## Project Structure

```
never-be-alone/
├── universal-context/
│   ├── webhook-server/           # Cloudflare Workers webhook server
│   │   ├── src/
│   │   │   ├── handlers/         # Audio & transcription webhook handlers
│   │   │   ├── services/         # Groq & Supermemory API clients
│   │   │   ├── utils/            # Audio conversion utilities
│   │   │   ├── types.ts          # TypeScript type definitions
│   │   │   └── index.ts          # Main worker entry point
│   │   ├── package.json
│   │   ├── wrangler.toml
│   │   ├── README.md             # Detailed documentation
│   │   ├── DEPLOYMENT.md         # Deployment guide
│   │   └── QUICK_START.md        # Quick start guide
│   ├── agent-layer/              # Fetch.ai agents (coming soon)
│   ├── docs/                     # Project documentation
│   └── scripts/                  # Utility scripts
├── .claude/                      # Claude Code configuration
└── README.md                     # This file
```

## Quick Start

### Prerequisites

- Node.js 18+
- Cloudflare account
- Groq API key
- Supermemory API key
- Omi wearable device

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Parth0248/never-be-alone.git
   cd never-be-alone
   ```

2. **Install webhook server**
   ```bash
   cd universal-context/webhook-server
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .dev.vars
   # Edit .dev.vars with your API keys
   ```

4. **Deploy to Cloudflare Workers**
   ```bash
   npm run deploy
   ```

5. **Configure Omi device**

   Set webhook URLs in the Omi app:
   - Audio: `https://your-worker.workers.dev/webhook/audio?sample_rate=16000&uid=YOUR_UID`
   - Transcription: `https://your-worker.workers.dev/webhook/transcription?uid=YOUR_UID`

For detailed instructions, see [`universal-context/webhook-server/QUICK_START.md`](universal-context/webhook-server/QUICK_START.md)

## Documentation

- **Webhook Server**: [`universal-context/webhook-server/README.md`](universal-context/webhook-server/README.md)
- **Deployment Guide**: [`universal-context/webhook-server/DEPLOYMENT.md`](universal-context/webhook-server/DEPLOYMENT.md)
- **Quick Start**: [`universal-context/webhook-server/QUICK_START.md`](universal-context/webhook-server/QUICK_START.md)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Omi Wearable Devices                        │
│              (DevKit 2 / Glass with Vision)                     │
└────────────┬─────────────────────────────┬────────────────────┘
             │                             │
             │ Audio Stream (5s chunks)    │ Pre-transcribed Text
             │                             │
             ▼                             ▼
┌────────────────────────┐    ┌────────────────────────┐
│  Audio Webhook         │    │ Transcription Webhook  │
│  /webhook/audio        │    │ /webhook/transcription │
└────────┬───────────────┘    └───────┬────────────────┘
         │                            │
         │ Convert PCM → WAV          │
         │                            │
         ▼                            │
┌────────────────────────┐            │
│  Groq Whisper-large-v3 │            │
│  (Transcription)       │            │
└────────┬───────────────┘            │
         │                            │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Supermemory API      │
         │   (Universal Storage)  │
         └────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Fetch.ai ASI:One      │
         │  (Agentic Layer)       │
         └────────────────────────┘
```

## Roadmap

### Phase 1: Core Infrastructure ✅
- [x] Cloudflare Workers webhook server
- [x] Audio format conversion (PCM → WAV)
- [x] Groq Whisper-large-v3 integration
- [x] Supermemory API integration
- [x] Dual webhook support (audio + transcription)
- [x] KV storage for temporary caching
- [x] Comprehensive documentation

### Phase 2: Hardware Integration 🚧
- [x] Omi DevKit 2 webhook integration
- [ ] Test with real Omi DevKit 2 device
- [ ] Omi Glass integration
- [ ] Vision processing for Glass

### Phase 3: Agentic Layer 📋
- [ ] Fetch.ai ASI:One integration
- [ ] Build intelligent agents
- [ ] Context-aware responses
- [ ] Multi-agent orchestration

### Phase 4: MCP Automation 📋
- [ ] Custom MCP server
- [ ] Automation workflows
- [ ] Tool integrations
- [ ] Submit for Best MCP Automation prize

## Cal Hacks 2025 - Sponsor Prizes

This project is targeting the following sponsor prizes:

1. **Anthropic/MCP** - Best MCP Automation Prize
   - Custom MCP server for workflow automation

2. **Supermemory** - Best use of Supermemory
   - Universal storage for all transcriptions and context

3. **Fetch.ai** - Best use of AI Agents
   - Agentic layer using ASI:One platform

4. **Groq** - Best use of Groq API
   - Whisper-large-v3 for real-time transcription

5. **Cloudflare** - Best use of Workers
   - Serverless webhook infrastructure

6. **Omi/Based Hardware** - Best Hardware Integration
   - Deep integration with DevKit 2 and Glass

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Team

Built with ❤️ at Cal Hacks 2025

## Acknowledgments

- **Groq** for providing Whisper-large-v3 API
- **Supermemory** for universal memory storage
- **Cloudflare** for Workers platform
- **Fetch.ai** for ASI:One agentic framework
- **Omi** for open-source wearable AI devices
- **Cal Hacks** for the amazing hackathon experience

## Contact

- GitHub: https://github.com/Parth0248/never-be-alone
- Issues: https://github.com/Parth0248/never-be-alone/issues
