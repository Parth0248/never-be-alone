"""Test script for agent orchestrator."""
import asyncio
import sys
from orchestrator import get_orchestrator


async def test_transcription(text: str):
    """Test processing a single transcription.

    Args:
        text: Transcription text to test
    """
    print(f"\n{'='*80}")
    print(f"Testing transcription: {text}")
    print(f"{'='*80}\n")

    orchestrator = get_orchestrator()

    # Process transcription
    result = await orchestrator.process_transcription(
        transcription=text,
        context={
            "uid": "test_user",
            "timestamp": "2025-10-25T14:30:00Z",
            "source": "test_script"
        }
    )

    # Print results
    print(f"Success: {result.get('success')}")
    print(f"Intent: {result.get('intent')}")
    print(f"Confidence: {result.get('confidence')}")
    print(f"\nEntities:")
    for key, value in result.get('entities', {}).items():
        print(f"  {key}: {value}")

    print(f"\nActions taken:")
    for action in result.get('actions_taken', []):
        print(f"  - {action}")

    print(f"\nDetailed results:")
    for agent_result in result.get('results', []):
        agent_type = agent_result.get('agent_type')
        action = agent_result.get('action')
        success = agent_result.get('success')
        message = agent_result.get('message', 'No message')

        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {agent_type}.{action}: {message}")

        if agent_result.get('result'):
            print(f"     Result: {agent_result['result']}")

    print(f"\n{'='*80}\n")


async def test_multiple_scenarios():
    """Test multiple scenarios."""
    test_cases = [
        "Remind me to call mom tomorrow at 3pm",
        "What did I say about the meeting last week?",
        "Turn on the living room lights",
        "Send an email to John about the project",
        "I'm feeling happy today",
        "Schedule a team meeting for next Monday at 10am",
        "What's the weather like today?",
        "Buy groceries tomorrow"
    ]

    for text in test_cases:
        await test_transcription(text)
        await asyncio.sleep(0.5)  # Small delay between tests


async def test_agent_status():
    """Test getting agent status."""
    print("\n" + "="*80)
    print("Agent Status")
    print("="*80 + "\n")

    orchestrator = get_orchestrator()
    status = orchestrator.get_agent_status()

    print(f"Total agents: {status.get('total_agents')}")
    print(f"ASI:One status: {status.get('asi_one_status')}")

    print("\nAvailable agents:")
    for name, info in status.get('agents', {}).items():
        print(f"\n  {name}:")
        print(f"    Description: {info.get('description')}")
        print(f"    Actions: {', '.join(info.get('actions', []))}")
        print(f"    Status: {info.get('status')}")

    print("\n" + "="*80 + "\n")


async def test_specific_agent(agent_type: str, action: str, params: dict):
    """Test a specific agent action.

    Args:
        agent_type: Type of agent
        action: Action to perform
        params: Parameters for the action
    """
    print(f"\n{'='*80}")
    print(f"Testing {agent_type}.{action}")
    print(f"{'='*80}\n")

    orchestrator = get_orchestrator()

    result = await orchestrator.test_agent(agent_type, action, params)

    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")

    if result.get('error'):
        print(f"Error: {result.get('error')}")

    if result.get('result'):
        print(f"\nResult:")
        for key, value in result['result'].items():
            print(f"  {key}: {value}")

    print(f"\n{'='*80}\n")


async def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print("Usage: python test_orchestrator.py <command> [args]")
        print("\nCommands:")
        print("  text <transcription>  - Test a single transcription")
        print("  all                   - Test multiple scenarios")
        print("  status                - Show agent status")
        print("  agent <type> <action> - Test specific agent")
        print("\nExamples:")
        print("  python test_orchestrator.py text 'Remind me to call mom tomorrow'")
        print("  python test_orchestrator.py all")
        print("  python test_orchestrator.py status")
        print("  python test_orchestrator.py agent calendar_agent create_reminder")
        return

    command = sys.argv[1]

    if command == "text":
        if len(sys.argv) < 3:
            print("Error: Please provide transcription text")
            return

        text = " ".join(sys.argv[2:])
        await test_transcription(text)

    elif command == "all":
        await test_multiple_scenarios()

    elif command == "status":
        await test_agent_status()

    elif command == "agent":
        if len(sys.argv) < 4:
            print("Error: Please provide agent_type and action")
            return

        agent_type = sys.argv[2]
        action = sys.argv[3]

        # Example params for different actions
        params_map = {
            "create_reminder": {
                "text": "Test reminder",
                "time": "tomorrow"
            },
            "search": {
                "query": "test query"
            },
            "classify": {
                "text": "This is a test"
            }
        }

        params = params_map.get(action, {})

        await test_specific_agent(agent_type, action, params)

    else:
        print(f"Unknown command: {command}")
        print("Use 'python test_orchestrator.py' without arguments for help")


if __name__ == "__main__":
    asyncio.run(main())
