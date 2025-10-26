"""Main Flask API server for agent orchestrator."""
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from orchestrator import get_orchestrator
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Get orchestrator instance
orchestrator = get_orchestrator()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "agent-orchestrator",
        "environment": Config.ENVIRONMENT
    })


@app.route('/orchestrate', methods=['POST'])
def orchestrate():
    """Main endpoint to process transcriptions through agent orchestration.

    Request body:
    {
        "transcription": "text from audio",
        "context": {
            "uid": "user123",
            "timestamp": "2025-10-25T14:30:00Z",
            "source": "omi_device"
        }
    }

    Returns:
        Agent orchestration results
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        transcription = data.get("transcription", "")

        if not transcription:
            return jsonify({
                "success": False,
                "error": "No transcription provided"
            }), 400

        context = data.get("context", {})

        # Process transcription asynchronously
        result = asyncio.run(
            orchestrator.process_transcription(transcription, context)
        )

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Error in /orchestrate endpoint: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/agents', methods=['GET'])
def list_agents():
    """List all available agents and their capabilities."""
    try:
        status = orchestrator.get_agent_status()
        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Error in /agents endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/test-agent', methods=['POST'])
def test_agent():
    """Test a specific agent action.

    Request body:
    {
        "agent_type": "calendar_agent",
        "action": "create_reminder",
        "params": {
            "text": "Call mom",
            "time": "tomorrow"
        }
    }

    Returns:
        Test result
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        agent_type = data.get("agent_type")
        action = data.get("action")
        params = data.get("params", {})

        if not agent_type or not action:
            return jsonify({
                "success": False,
                "error": "agent_type and action are required"
            }), 400

        # Test agent
        result = asyncio.run(
            orchestrator.test_agent(agent_type, action, params)
        )

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error in /test-agent endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Get detailed capabilities of a specific agent.

    Query params:
        agent_type: Type of agent (optional, returns all if not specified)

    Returns:
        Agent capabilities
    """
    try:
        agent_type = request.args.get("agent_type")

        if agent_type:
            agent = orchestrator.agents.get(agent_type)

            if not agent:
                return jsonify({
                    "success": False,
                    "error": f"Agent not found: {agent_type}"
                }), 404

            capabilities = agent.get_capabilities()
            return jsonify({
                "success": True,
                "agent_type": agent_type,
                "capabilities": capabilities
            }), 200

        else:
            # Return capabilities for all agents
            all_capabilities = {}

            for name, agent in orchestrator.agents.items():
                all_capabilities[name] = agent.get_capabilities()

            return jsonify({
                "success": True,
                "agents": all_capabilities
            }), 200

    except Exception as e:
        logger.error(f"Error in /capabilities endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/process-batch', methods=['POST'])
def process_batch():
    """Process multiple transcriptions in batch.

    Request body:
    {
        "transcriptions": [
            {
                "transcription": "text 1",
                "context": {...}
            },
            {
                "transcription": "text 2",
                "context": {...}
            }
        ]
    }

    Returns:
        Batch processing results
    """
    try:
        data = request.get_json()

        if not data or "transcriptions" not in data:
            return jsonify({
                "success": False,
                "error": "No transcriptions provided"
            }), 400

        transcriptions = data.get("transcriptions", [])

        if not isinstance(transcriptions, list):
            return jsonify({
                "success": False,
                "error": "transcriptions must be a list"
            }), 400

        # Process all transcriptions
        results = []

        for item in transcriptions:
            transcription = item.get("transcription", "")
            context = item.get("context", {})

            if transcription:
                result = asyncio.run(
                    orchestrator.process_transcription(transcription, context)
                )
                results.append(result)

        return jsonify({
            "success": True,
            "count": len(results),
            "results": results
        }), 200

    except Exception as e:
        logger.error(f"Error in /process-batch endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    logger.info(f"Starting Agent Orchestrator on port {Config.PORT}")
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    logger.info(f"Available agents: {list(orchestrator.agents.keys())}")

    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=(Config.ENVIRONMENT == 'development')
    )
