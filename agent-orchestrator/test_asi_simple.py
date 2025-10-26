#!/usr/bin/env python3
"""
Simple test for ASI:One Agentic + Omi Client integration
Tests the complete flow without emoji issues
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import get_orchestrator


async def test_complex_task_flow():
    """Test complex task with ASI:One agentic and Omi output."""
    print("\n" + "="*80)
    print("TEST: Complex Task Flow (ASI:One Agentic + Omi Client)")
    print("="*80 + "\n")

    orchestrator = get_orchestrator()

    # Test case: Complex reminder that should trigger agentic layer
    transcription = "Remind me tomorrow at 2pm to call mom about her birthday gift"
    context = {
        "uid": "test_user_123",
        "timestamp": "2025-10-26T10:00:00Z",
        "source": "test"
    }

    print(f"Transcription: {transcription}")
    print(f"Context: {context}\n")
    print("Expected Flow:")
    print("  1. Reka processes text")
    print("  2. ASI:One analyzes intent")
    print("  3. Routes to ASI:One Agentic (complex task)")
    print("  4. Sends response via Omi Client")
    print("  5. Stores in Supermemory")
    print("\n" + "-"*80 + "\n")

    try:
        result = await orchestrator.process_transcription(transcription, context)

        print("\n" + "-"*80)
        print("RESULTS:")
        print("-"*80)
        print(f"Success: {result.get('success')}")
        print(f"Intent: {result.get('intent')}")
        print(f"Confidence: {result.get('confidence')}")

        # Check if agentic was used
        results = result.get('results', [])
        used_agentic = any(r.get('agent_type') == 'asi_one_agentic' for r in results)

        print(f"\nASI:One Agentic Called: {'YES' if used_agentic else 'NO'}")

        if used_agentic:
            agentic_result = next(r for r in results if r.get('agent_type') == 'asi_one_agentic')
            print(f"Model Used: {agentic_result.get('message', 'N/A')}")
            print(f"Agents Used: {agentic_result.get('agents_used', [])}")

            if agentic_result.get('response'):
                response = agentic_result.get('response')
                print(f"\nResponse (first 200 chars):")
                print(f"  {response[:200]}...")

        print(f"\nActions Taken: {result.get('actions_taken', [])}")

        print("\n" + "="*80)
        if result.get('success') and used_agentic:
            print("TEST PASSED: Complex task successfully routed through agentic layer!")
        elif result.get('success') and not used_agentic:
            print("WARNING: Task completed but did NOT use agentic layer")
        else:
            print("TEST FAILED: Processing error")
        print("="*80 + "\n")

        return result.get('success') and used_agentic

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        print("TEST FAILED: Exception occurred")
        print("="*80 + "\n")
        return False


async def test_simple_query():
    """Test simple query that should NOT use agentic layer."""
    print("\n" + "="*80)
    print("TEST: Simple Query (No Agentic)")
    print("="*80 + "\n")

    orchestrator = get_orchestrator()

    transcription = "What did I talk about yesterday?"
    context = {
        "uid": "test_user_123",
        "timestamp": "2025-10-26T10:00:00Z",
        "source": "test"
    }

    print(f"Transcription: {transcription}")
    print(f"Expected: Should NOT use ASI:One agentic\n")

    try:
        result = await orchestrator.process_transcription(transcription, context)

        results = result.get('results', [])
        used_agentic = any(r.get('agent_type') == 'asi_one_agentic' for r in results)

        print(f"\nASI:One Agentic Called: {'YES' if used_agentic else 'NO'}")
        print(f"Intent: {result.get('intent')}")

        if not used_agentic:
            print("\nTEST PASSED: Simple query handled without agentic layer!")
        else:
            print("\nWARNING: Simple query incorrectly used agentic layer")

        return not used_agentic

    except Exception as e:
        print(f"\nERROR: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("ASI:ONE AGENTIC + OMI CLIENT INTEGRATION TEST")
    print("="*80)

    # Test 1: Complex task
    test1_passed = await test_complex_task_flow()

    # Test 2: Simple query
    test2_passed = await test_simple_query()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Test 1 (Complex Task): {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Test 2 (Simple Query): {'PASSED' if test2_passed else 'FAILED'}")
    print("="*80 + "\n")

    return test1_passed and test2_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
