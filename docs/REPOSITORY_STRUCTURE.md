# Repository Structure

Clean, organized repository structure for the Never Be Alone project.

## 📁 Directory Structure

```
never-be-alone/
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── run_tests.py                  # Test runner script
│
├── Core Application Files
├── reka_client.py                # Reka.AI multimodal API client
├── omi_client.py                 # OMI App API client
├── webhook_server.py             # Flask webhook server
│
├── Documentation
├── README.md                     # Main project documentation
├── QUICK_START_REKA.md          # Quick start guide for Reka integration
├── REKA_INTEGRATION_GUIDE.md    # Detailed Reka integration guide
├── OMI_API_TEST_RESULTS.md      # OMI API test results
├── SETUP_API_KEYS.md            # API key setup instructions
├── REPOSITORY_STRUCTURE.md      # This file
│
├── Planning & Architecture
├── AGENT_ORCHESTRATION_ARCHITECTURE.md
├── AGENT_ORCHESTRATION_COMPLETE.md
├── INTEGRATION_OPTIONS_COMPARISON.md
├── PHASE2_PLAN.md
├── ROADMAP_SUMMARY.md
├── QUICK_START_AGENT_IMPLEMENTATION.md
├── SPECTACLES_INTEGRATION_READY.md
├── HOW_TO_VIEW_LOGS_AND_TRANSCRIPTIONS.md
├── OMI_TRANSCRIPTION_SETUP.md
├── planning.txt
│
├── Media
├── RekaArchitecture.png         # Architecture diagram
│
├── tests/                        # Test scripts (git ignored)
│   ├── README.md                 # Test documentation
│   ├── test_omi_apis.py          # OMI API tests
│   ├── test_reka_integration.py  # Reka integration tests
│   ├── test_*.py                 # Legacy test scripts
│   ├── view_*.py                 # Utility scripts
│   └── *.sh                      # Shell test scripts
│
├── archive/                      # Test data & archived files (git ignored)
│   ├── README.md                 # Archive documentation
│   ├── webhook.json              # Sample OMI webhook data (~2.8MB)
│   ├── test_audio.wav            # Sample audio file
│   ├── transcription_result.json # Sample transcription
│   ├── captured_image.jpg        # Sample image
│   └── *.mp4, *.txt              # Other archived files
│
├── agent-orchestrator/           # Agent orchestration system
│   └── (separate module)
│
└── universal-context/            # Universal context system
    └── (separate module)
```

## 🎯 Core Files

### Application Code

- **`reka_client.py`** - Reka.AI API client
  - Handles multimodal processing (images + audio + text)
  - Supports simple queries and complex OMI data processing
  - Uses reka-flash model by default

- **`omi_client.py`** - OMI App API client
  - Send notifications, conversations, memories
  - Read conversations and memories
  - Full CRUD operations for OMI app

- **`webhook_server.py`** - Flask webhook server
  - Endpoints: `/webhook/audio`, `/webhook/images`, `/webhook/combined`
  - Combines audio + images received within 60 seconds
  - Processes through Reka → sends to OMI app

### Configuration

- **`.env`** - Environment variables
  ```
  REKA_API_KEY=...
  OMI_API_KEY=...
  OMI_APP_ID=...
  OMI_USER_ID=...
  SUPERMEMORY_API_KEY=...
  GROQ_API_KEY=...
  PORT=3000
  ```

- **`requirements.txt`** - Python dependencies
  ```
  flask
  requests
  python-dotenv
  Pillow
  groq
  ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test
python tests/test_omi_apis.py
python tests/test_reka_integration.py
```

### Test Files

Located in `tests/` directory:
- `test_omi_apis.py` - 6 tests for OMI API operations
- `test_reka_integration.py` - 3 tests for Reka integration
- Legacy test scripts for various components

## 📦 Archive

The `archive/` directory contains:
- Sample test data (webhook.json, test_audio.wav)
- Archived documentation
- Temporary files
- Large binary files

Both `tests/` and `archive/` are git-ignored.

## 🔒 Git Ignore Rules

The `.gitignore` file excludes:
- Python artifacts (`__pycache__`, `*.pyc`)
- Environment files (`.env`)
- IDE files (`.vscode`, `.idea`)
- **Test directory** (`tests/`)
- **Archive directory** (`archive/`)
- Large media files (`*.mp4`, `*.wav`, `*.mp3`)
- JSON data files (except config files)
- Logs and temporary files

## 📚 Documentation Organization

### Quick Start
- `QUICK_START_REKA.md` - Get started quickly with Reka integration
- `SETUP_API_KEYS.md` - API key configuration

### Detailed Guides
- `REKA_INTEGRATION_GUIDE.md` - Complete Reka.AI integration guide
- `OMI_API_TEST_RESULTS.md` - OMI API testing documentation
- `README.md` - Main project overview

### Architecture & Planning
- `AGENT_ORCHESTRATION_ARCHITECTURE.md` - System architecture
- `PHASE2_PLAN.md` - Project phases and milestones
- `ROADMAP_SUMMARY.md` - Development roadmap
- Various integration and planning documents

## 🚀 Deployment

### Local Development
```bash
python webhook_server.py
```

### Production
- Deploy to Railway, Heroku, or Google Cloud Run
- Update OMI webhook URLs to point to your server
- Set environment variables in hosting platform

## 🔄 Import Structure

Tests use relative imports:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reka_client import RekaClient
from omi_client import OmiClient
```

Application files import directly from the root.

## 🛠️ Maintenance

### Adding New Tests
1. Create test file in `tests/` directory
2. Add path setup for imports (see existing tests)
3. Update `tests/README.md`
4. Optionally add to `run_tests.py`

### Adding New Documentation
- Place in root directory
- Add to appropriate section in this file
- Update main `README.md` if necessary

### Managing Archive
- Move large files, test data, and temporary files to `archive/`
- Update `archive/README.md` if needed
- These files won't be committed to git

## 📝 Notes

- All test scripts have been updated with proper import paths
- Environment variables loaded from project root `.env`
- Tests can access sample data in `archive/webhook.json`
- UTF-8 encoding issues handled by test runner

---

Last updated: October 26, 2025
