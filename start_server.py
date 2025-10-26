"""
Start the OMI Webhook Server
Main entry point for the application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the webhook server
if __name__ == '__main__':
    from src.webhook_server import app

    port = int(os.getenv('PORT', 3000))

    print("=" * 60)
    print("OMI WEBHOOK SERVER STARTING")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"\nEndpoints:")
    print(f"  - POST /webhook/audio - Receive audio transcripts")
    print(f"  - POST /webhook/images - Receive images and context")
    print(f"  - POST /webhook/combined - Receive combined data")
    print(f"  - GET  /health - Health check")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
