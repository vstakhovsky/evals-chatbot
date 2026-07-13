#!/usr/bin/env python3
"""
Shared routing parse function — used by pipeline, subset runner, and notebook.

Design per spec 07: Every bot response must start with "ACTION: answer" or "ACTION: escalate"
on the first line. Malformed/missing → format_violation counter (treat as answer).

This function is imported everywhere — NEVER reimplement.
"""

import re


def parse_action(bot_response):
    """
    Parse ACTION line from bot response.

    Returns: ('answer' | 'escalate' | 'format_violation')

    Expected format:
        ACTION: answer
        <rest of response>

    OR:
        ACTION: escalate
        <rest of response>

    Malformed/missing line → format_violation (treat as answer)
    """
    if not bot_response:
        return 'format_violation'

    # Get first line
    first_line = bot_response.split('\n')[0].strip()

    # Parse ACTION line
    action_match = re.match(r'^ACTION:\s*(answer|escalate)\s*$', first_line, re.IGNORECASE)

    if action_match:
        return action_match.group(1).lower()
    else:
        return 'format_violation'


def strip_action_line(bot_response):
    """
    Strip ACTION line from bot response for user-facing display.
    Returns response without the first ACTION line.
    """
    if not bot_response:
        return bot_response

    lines = bot_response.split('\n', 1)  # Split only on first newline
    if len(lines) == 2:
        return lines[1].strip()
    else:
        return bot_response


def unit_test():
    """Unit tests for parse_action function."""
    print("=" * 60)
    print("ROUTING PARSE UNIT TESTS")
    print("=" * 60)

    # Test escalate
    escalate_response = "ACTION: escalate\nI understand your concern. Please contact our support team for assistance with this matter."
    result = parse_action(escalate_response)
    assert result == 'escalate', f"Expected 'escalate', got '{result}'"
    print("✓ Escalate parse test passed")

    # Test answer
    answer_response = "ACTION: answer\nTo freeze your card, follow these steps: Go to Settings > Cards > Freeze."
    result = parse_action(answer_response)
    assert result == 'answer', f"Expected 'answer', got '{result}'"
    print("✓ Answer parse test passed")

    # Test missing line (format violation)
    no_action_response = "To freeze your card, follow these steps: Go to Settings > Cards > Freeze."
    result = parse_action(no_action_response)
    assert result == 'format_violation', f"Expected 'format_violation', got '{result}'"
    print("✓ Missing ACTION line test passed")

    # Test malformed line (format violation)
    malformed_response = "ACTION: something_else\nHere is the answer."
    result = parse_action(malformed_response)
    assert result == 'format_violation', f"Expected 'format_violation', got '{result}'"
    print("✓ Malformed ACTION line test passed")

    # Test case insensitive
    uppercase_response = "ACTION: ESCALATE\nPlease contact support."
    result = parse_action(uppercase_response)
    assert result == 'escalate', f"Expected 'escalate', got '{result}'"
    print("✓ Case insensitive test passed")

    # Test strip_action_line
    test_response = "ACTION: answer\nTo freeze your card: Go to Settings."
    stripped = strip_action_line(test_response)
    assert "ACTION:" not in stripped, "ACTION line not stripped"
    assert stripped == "To freeze your card: Go to Settings.", f"Wrong stripped content: {stripped}"
    print("✓ Strip ACTION line test passed")

    print("=" * 60)
    print("✅ ALL ROUTING PARSE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    unit_test()
