"""
Test Runner for Never Be Alone Project
Run tests with proper encoding and path setup
"""

import sys
import os
import subprocess

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def run_test(test_file, description):
    """Run a test file and return success status"""
    print("\n" + "=" * 60)
    print(f"Running: {description}")
    print("=" * 60 + "\n")

    try:
        # Force UTF-8 encoding for subprocess
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            encoding='utf-8',
            timeout=120,
            env=env
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"X Test timed out: {test_file}")
        return False
    except Exception as e:
        print(f"X Error running test: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("NEVER BE ALONE - TEST SUITE")
    print("🚀" * 30 + "\n")

    tests = [
        ("tests/test_omi_apis.py", "OMI API Integration Tests"),
        ("tests/test_reka_integration.py", "Reka.AI Integration Tests"),
    ]

    results = []

    for test_file, description in tests:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            results.append((description, False))
            continue

        success = run_test(test_file, description)
        results.append((description, success))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed

    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {description}")

    print(f"\nTotal: {len(results)} test suites")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TEST SUITES PASSED!")
    else:
        print(f"\n⚠️  {failed} test suite(s) failed")

    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
