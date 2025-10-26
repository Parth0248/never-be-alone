"""Configuration management for agent orchestrator."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for agent orchestrator."""

    # ASI:One Configuration
    ASI_ONE_API_KEY = os.getenv('ASI_ONE_API_KEY')
    ASI_ONE_BASE_URL = "https://api.asi1.ai/v1"

    # Agentverse Configuration
    AGENTVERSE_API_KEY = os.getenv('AGENTVERSE_API_KEY')
    AGENTVERSE_MCP_URL = os.getenv('AGENTVERSE_MCP_URL', 'https://mcp.agentverse.ai/sse')
    AGENTVERSE_BASE_URL = "https://agentverse.ai/v1"

    # Supermemory Configuration
    SUPERMEMORY_API_KEY = os.getenv('SUPERMEMORY_API_KEY')
    SUPERMEMORY_BASE_URL = "https://api.supermemory.ai"

    # Reka.ai Configuration
    REKA_API_KEY = os.getenv('REKA_API_KEY')
    REKA_BASE_URL = "https://api.reka.ai"
    REKA_MODEL = os.getenv('REKA_MODEL', 'reka-core')  # reka-core, reka-flash, reka-edge

    # Groq Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'calhacks-omi-audio')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    # Server Configuration
    PORT = int(os.getenv('PORT', 8080))
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    # Agent Configuration
    AGENT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required = [
            'ASI_ONE_API_KEY',
            'AGENTVERSE_API_KEY',
            'SUPERMEMORY_API_KEY',
        ]

        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        # Warn about optional configs
        if not cls.REKA_API_KEY:
            print("⚠️  REKA_API_KEY not set - Reka.ai enhancement will be skipped")

        return True

# Validate configuration on import
Config.validate()
