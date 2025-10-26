#!/usr/bin/env python3
"""
Test script for ASI:One Agentic Integration
Tests the complete flow: Reka → ASI:One Agentic → Omi Client → Supermemory
"""
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asi_one_agentic_client import ASIOneAgenticClient
from orchestrator import get_orchestrator


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_result(result: dict, label: str = "Result"):
    """Print formatted result."""
    print(f"\n{label}:")
    print(f"  Success: {result.get('success')}")
    if result.get('success'):
        if 'response' in result:
            print(f"  Response: {result['response'][:200]}...")
        if 'model_used' in result:
            print(f"  Model: {result['model_used']}")
        if 'complexity_score' in result:
            print(f"  Complexity: {result['complexity_score']}/10")
        if 'agents_used' in result and result['agents_used']:
            print(f"  Agents: {', '.join(result['agents_used'])}")
    else:
        print(f"  Error: {result.get('error')}")


async def test_1_simple_query():
    """Test 1: Simple query (should NOT use agentic layer)."""
    print_header("TEST 1: Simple Query (No Agentic)")

    orchestrator = get_orchestrator()

    transcription = "What's the weather like today?"
    context = {
        "uid": "test_user_123",
        "timestamp": "2025-10-26T10:00:00Z",
        "source": "test"
    }

    print(f"📝 Transcription: {transcription}")
    print(f"🎯 Expected: Should use simple routing, NOT ASI:One agentic\n")

    result = await orchestrator.process_transcription(transcription, context)

    print_result(result, "Pipeline Result")

    # Check that it didn't use agentic
    used_agentic = any(
        r.get("agent_type") == "asi_one_agentic"
        for r in result.get("results", [])
    )

    if not used_agentic:
        print(f"\n✅ TEST 1 PASSED: Simple query handled without agentic layer")
    else:
        print(f"\n❌ TEST 1 FAILED: Simple query incorrectly routed to agentic layer")

    return not used_agentic


async def test_2_complex_reminder():
    """Test 2: Complex reminder task (should use agentic layer)."""
    print_header("TEST 2: Complex Reminder (With Agentic)")

    orchestrator = get_orchestrator()

    transcription = "Remind me tomorrow at 2pm to call mom about her birthday gift, and also send her an email tonight"
    context = {
        "uid": "test_user_123",
        "timestamp": "2025-10-26T10:00:00Z",
        "source": "test"
    }

    print(f"📝 Transcription: {transcription}")
    print(f"🎯 Expected: Should use ASI:One agentic for multi-step orchestration\n")

    result = await orchestrator.process_transcription(transcription, context)

    print_result(result, "Pipeline Result")

    # Check that it used agentic
    used_agentic = any(
        r.get("agent_type") == "asi_one_agentic"
        for r in result.get("results", [])
    )

    if used_agentic:
        print(f"\n✅ TEST 2 PASSED: Complex task routed to agentic layer")
    else:
        print(f"\n❌ TEST 2 FAILED: Complex task NOT routed to agentic layer")

    return used_agentic


async def test_3_direct_agentic_call():
    """Test 3: Direct ASI:One agentic client call."""
    print_header("TEST 3: Direct ASI:One Agentic Call")

    client = ASIOneAgenticClient()

    text = "Schedule a meeting with the design team next Tuesday at 3pm, and book the conference room"
    entities = {
        "time": "next Tuesday at 3pm",
        "people": ["design team"],
        "action": "schedule meeting"
    }

    print(f"📝 Text: {text}")
    print(f"🎯 Expected: Should use asi1-agentic or asi1-extended-agentic\n")

    result = client.process_complex_task(
        text=text,
        entities=entities,
        intent="complex_scheduling",
        conversation_id="test_conv_123"
    )

    print_result(result, "Agentic Result")

    if result.get('success'):
        print(f"\n✅ TEST 3 PASSED: Direct agentic call successful")
        return True
    else:
        print(f"\n❌ TEST 3 FAILED: Direct agentic call failed")
        return False


async def test_4_complexity_scoring():
    """Test 4: Complexity scoring system."""
    print_header("TEST 4: Complexity Scoring")

    client = ASIOneAgenticClient()

    test_cases = [
        {
            "text": "Hello",
            "entities": {},
            "intent": "observation",
            "expected_range": (1, 3),
            "expected_model": "asi1-fast-agentic"
        },
        {
            "text": "What did I talk about yesterday with Sarah?",
            "entities": {"person": "Sarah", "time": "yesterday"},
            "intent": "search_info",
            "expected_range": (2, 4),
            "expected_model": "asi1-fast-agentic"
        },
        {
            "text": "Remind me tomorrow at 10am to call the dentist, and also schedule a follow-up appointment for next month",
            "entities": {
                "time": ["tomorrow at 10am", "next month"],
                "action": ["call", "schedule"],
                "person": "dentist"
            },
            "intent": "complex_scheduling",
            "expected_range": (7, 10),
            "expected_model": "asi1-extended-agentic"
        }
    ]

    all_passed = True

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Text: {test['text'][:60]}...")
        print(f"  Intent: {test['intent']}")

        complexity = client.calculate_complexity(
            test["text"],
            test["entities"],
            test["intent"]
        )

        model = client.select_model(complexity, multi_agent=complexity >= 8)

        print(f"  Complexity: {complexity}/10")
        print(f"  Model: {model}")
        print(f"  Expected: {test['expected_range'][0]}-{test['expected_range'][1]}, {test['expected_model']}")

        in_range = test["expected_range"][0] <= complexity <= test["expected_range"][1]
        # Model can be upgraded for multi-agent, so just check it's not downgraded
        model_ok = model in ["asi1-agentic", "asi1-extended-agentic"] if complexity >= 4 else True

        if in_range and model_ok:
            print(f"  ✅ Passed")
        else:
            print(f"  ❌ Failed")
            all_passed = False

    if all_passed:
        print(f"\n✅ TEST 4 PASSED: All complexity calculations correct")
    else:
        print(f"\n❌ TEST 4 FAILED: Some complexity calculations incorrect")

    return all_passed


async def test_5_multimodal_support():
    """Test 5: Multimodal support (images + text)."""
    print_header("TEST 5: Multimodal Support")

    client = ASIOneAgenticClient()

    # Simulate base64 image (just a placeholder)
    fake_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    text = "What do you see in this image? Can you help me organize what's visible?"
    reka_understanding = {
        "enhanced_understanding": "User is showing a cluttered desk with papers and a laptop",
        "entities": {
            "objects": ["desk", "papers", "laptop"],
            "context": "workspace organization"
        }
    }

    print(f"📝 Text: {text}")
    print(f"🖼️  Images: 1 image provided")
    print(f"🤖 Reka Understanding: {reka_understanding['enhanced_understanding']}\n")

    result = client.process_complex_task(
        text=text,
        images_base64=[fake_image],
        entities=reka_understanding["entities"],
        intent="workflow_automation",
        reka_understanding=reka_understanding,
        conversation_id="test_multimodal_123"
    )

    print_result(result, "Multimodal Result")

    if result.get('success'):
        print(f"\n✅ TEST 5 PASSED: Multimodal call successful")
        return True
    else:
        print(f"\n⚠️  TEST 5: Multimodal call completed with status: {result.get('error')}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("\n" + "🚀" * 40)
    print("ASI:ONE AGENTIC INTEGRATION TEST SUITE")
    print("🚀" * 40)

    results = []

    # Run tests
    try:
        results.append(("Simple Query", await test_1_simple_query()))
    except Exception as e:
        print(f"\n❌ TEST 1 EXCEPTION: {e}")
        results.append(("Simple Query", False))

    try:
        results.append(("Complex Reminder", await test_2_complex_reminder()))
    except Exception as e:
        print(f"\n❌ TEST 2 EXCEPTION: {e}")
        results.append(("Complex Reminder", False))

    try:
        results.append(("Direct Agentic Call", await test_3_direct_agentic_call()))
    except Exception as e:
        print(f"\n❌ TEST 3 EXCEPTION: {e}")
        results.append(("Direct Agentic Call", False))

    try:
        results.append(("Complexity Scoring", await test_4_complexity_scoring()))
    except Exception as e:
        print(f"\n❌ TEST 4 EXCEPTION: {e}")
        results.append(("Complexity Scoring", False))

    try:
        results.append(("Multimodal Support", await test_5_multimodal_support()))
    except Exception as e:
        print(f"\n❌ TEST 5 EXCEPTION: {e}")
        results.append(("Multimodal Support", False))

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}  {name}")

    print(f"\n{'='*80}")
    print(f"  TOTAL: {passed}/{total} tests passed")
    print(f"{'='*80}\n")

    return passed == total


if __name__ == "__main__":
    print("\n🔧 Starting ASI:One Agentic Integration Tests...\n")

    success = asyncio.run(run_all_tests())

    if success:
        print("✅ ALL TESTS PASSED! ASI:One agentic integration is working correctly.\n")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED. Please review the output above.\n")
        sys.exit(1)
