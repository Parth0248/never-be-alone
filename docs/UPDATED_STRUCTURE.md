# Updated Repository Structure

**Last Updated:** October 26, 2025

## 📁 New Directory Structure

```
never-be-alone/
├── .env                      # Environment variables (git-ignored)
├── .env.example              # Example environment file
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── README.md                 # Main project documentation
├── CLAUDE.md                 # Claude integration notes
│
├── 🚀 Entry Points
├── start_server.py           # Main server entry point
├── run_tests.py              # Test runner
│
├── 📦 src/                   # Source code (application modules)
│   ├── __init__.py           # Package initialization
│   ├── reka_client.py        # Reka.AI API client
│   ├── omi_client.py         # OMI App API client
│   └── webhook_server.py     # Flask webhook server
│
├── 📚 docs/                  # Documentation
│   ├── QUICK_START_REKA.md
│   ├── REKA_INTEGRATION_GUIDE.md
│   ├── OMI_API_TEST_RESULTS.md
│   ├── SETUP_API_KEYS.md
│   ├── REPOSITORY_STRUCTURE.md
│   ├── CLEANUP_SUMMARY.md
│   ├── UPDATED_STRUCTURE.md (this file)
│   ├── HOW_TO_VIEW_LOGS_AND_TRANSCRIPTIONS.md
│   ├── OMI_TRANSCRIPTION_SETUP.md
│   ├── SPECTACLES_INTEGRATION_READY.md
│   └── RekaArchitecture.png
│
├── 📋 planning/              # Planning & architecture docs
│   ├── AGENT_ORCHESTRATION_ARCHITECTURE.md
│   ├── AGENT_ORCHESTRATION_COMPLETE.md
│   ├── INTEGRATION_OPTIONS_COMPARISON.md
│   ├── PHASE2_PLAN.md
│   ├── ROADMAP_SUMMARY.md
│   ├── QUICK_START_AGENT_IMPLEMENTATION.md
│   └── planning.txt
│
├── 🧪 tests/                 # Test scripts (git-ignored)
│   ├── README.md
│   ├── test_omi_apis.py
│   ├── test_reka_integration.py
│   └── ... (other test files)
│
├── 📦 archive/               # Archived files & test data (git-ignored)
│   ├── README.md
│   ├── webhook.json          # Sample webhook data (2.8MB)
│   └── ... (test data files)
│
├── 🤖 agent-orchestrator/    # Agent orchestration system
│   └── (separate module)
│
└── 🌐 universal-context/     # Universal context system
    └── (separate module)
```

## 🎯 Key Changes from Previous Structure

### 1. **Source Code Organized** ✨
All Python application code moved to `src/`:
- `src/reka_client.py`
- `src/omi_client.py`
- `src/webhook_server.py`
- `src/__init__.py` (package initialization)

### 2. **Documentation Organized** ✨
All `.md` documentation files moved to `docs/`:
- Setup guides
- Integration guides
- Test results
- Architecture diagrams

### 3. **Planning Separated** ✨
All planning and architecture docs moved to `planning/`:
- Architecture documents
- Roadmaps
- Phase plans
- Integration comparisons

### 4. **Clean Root Directory** ✨
Root now contains only:
- Configuration files (`.env`, `requirements.txt`)
- Entry points (`start_server.py`, `run_tests.py`)
- Main README
- Project folders

## 🚀 How to Use

### Starting the Server

```bash
# New way (recommended)
python start_server.py

# Or directly
python -m src.webhook_server
```

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test
python tests/test_omi_apis.py
python tests/test_reka_integration.py
```

### Importing Modules

```python
# In application code
from src.reka_client import RekaClient
from src.omi_client import OmiClient

# Or using package import
from src import RekaClient, OmiClient
```

## 📦 Import Structure

### From Root Directory

```python
from src.reka_client import RekaClient
from src.omi_client import OmiClient
```

### From Tests

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reka_client import RekaClient
from src.omi_client import OmiClient
```

### Within src/

```python
# webhook_server.py imports
from src.reka_client import RekaClient
from src.omi_client import OmiClient
```

## 📚 Documentation Locations

| Document | Location |
|----------|----------|
| Quick Start Guide | `docs/QUICK_START_REKA.md` |
| Full Integration Guide | `docs/REKA_INTEGRATION_GUIDE.md` |
| API Test Results | `docs/OMI_API_TEST_RESULTS.md` |
| Setup Instructions | `docs/SETUP_API_KEYS.md` |
| Architecture Diagram | `docs/RekaArchitecture.png` |
| This Document | `docs/UPDATED_STRUCTURE.md` |

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Reka.AI
REKA_API_KEY=your_key
REKA_MODEL=reka-flash

# OMI App
OMI_API_KEY=your_key
OMI_APP_ID=your_id
OMI_USER_ID=your_user_id

# Supermemory
SUPERMEMORY_API_KEY=your_key

# Groq (for audio transcription)
GROQ_API_KEY=your_key

# Server
PORT=3000
```

### Dependencies (requirements.txt)
```
flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
Pillow==12.0.0
groq==0.4.2
gunicorn==21.2.0
pytest==7.4.3
```

## 🔒 Git Ignore Rules

The following are git-ignored:
- `tests/` - All test files
- `archive/` - Test data and archived files
- `src/__pycache__/` - Python cache in src
- `__pycache__/` - Root Python cache
- `.env` - Environment variables
- `*.pyc`, `*.pyo` - Python compiled files
- Large media files (*.mp4, *.wav, etc.)

## ✅ Benefits of New Structure

1. **Professional Organization**
   - Clear separation: code, docs, tests, planning
   - Industry-standard Python package structure
   - Easy to navigate and understand

2. **Better Maintainability**
   - Source code isolated in `src/`
   - Documentation grouped in `docs/`
   - Planning materials separate

3. **Cleaner Imports**
   - Package-based imports with `src.`
   - Clear module hierarchy
   - Easier dependency management

4. **Scalability**
   - Easy to add new modules to `src/`
   - Documentation naturally organized
   - Test structure supports growth

5. **Git Efficiency**
   - Only essential code committed
   - No test data in repository
   - Smaller repository size

## 🚀 Migration Notes

### For Developers

If you had the old structure:
1. Update imports to use `from src.` prefix
2. Use `start_server.py` instead of running `webhook_server.py` directly
3. Documentation now in `docs/` folder
4. Planning docs in `planning/` folder

### For CI/CD

Update deployment scripts:
```bash
# Old way
python webhook_server.py

# New way
python start_server.py
```

## 📝 Next Steps

1. ✅ All files organized
2. ✅ Imports updated
3. ✅ Documentation moved
4. ✅ Git ignore configured
5. ⏳ Test that everything works
6. ⏳ Deploy with new structure

---

**Status:** Ready for production! 🎉
