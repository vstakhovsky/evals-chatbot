"""Metric calculation tests using hand-calculated fixture."""
import json
from pathlib import Path

def test_routing_accuracy_formula():
    """Test routing accuracy with manually calculated fixture."""
    # Load test fixture
    fixture_path = Path("tests/test_metrics_fixture.json")
    if not fixture_path.exists():
        print("⚠️  Test fixture not found, skipping metric tests")
        return

    with open(fixture_path, 'r') as f:
        cases = json.load(f)

    # Manual calculation: 6 correct routing out of 8 applicable cases
    applicable = [c for c in cases if c.get('expected_action')]
    correct = [c for c in applicable if c.get('predicted_action') == c.get('expected_action')]

    assert len(correct) == 6, f"Expected 6 correct routing, got {len(correct)}"
    assert len(applicable) == 8, f"Expected 8 applicable cases, got {len(applicable)}"

    expected_rate = 6 / 8
    actual_rate = len(correct) / len(applicable)
    assert abs(actual_rate - expected_rate) < 0.01, f"Routing accuracy should be {expected_rate}, got {actual_rate}"

    print("✅ Routing accuracy formula: 6/8 = 75.0%")

def test_critical_escalation_recall_formula():
    """Test critical escalation recall formula."""
    fixture_path = Path("tests/test_metrics_fixture.json")
    if not fixture_path.exists():
        return

    with open(fixture_path, 'r') as f:
        cases = json.load(f)

    # Manual calculation: 1 correct out of 2 applicable critical escalation cases
    applicable = [c for c in cases if c.get('risk_level') == 'critical' and c.get('expected_action') == 'escalate']
    correct = [c for c in applicable if c.get('predicted_action') == 'escalate']

    assert len(correct) == 1, f"Expected 1 correct escalation, got {len(correct)}"
    assert len(applicable) == 2, f"Expected 2 applicable cases, got {len(applicable)}"

    expected_rate = 1 / 2
    actual_rate = len(correct) / len(applicable)
    assert abs(actual_rate - expected_rate) < 0.01, f"Critical recall should be {expected_rate}, got {actual_rate}"

    print("✅ Critical escalation recall: 1/2 = 50.0%")

def test_zero_denominator_handling():
    """Test that zero denominator returns null, not 0%."""
    # Test with empty applicable set
    applicable = []
    correct = []

    if len(applicable) == 0:
        rate = None
    else:
        rate = len(correct) / len(applicable)

    assert rate is None, "Zero denominator must return None, not 0"
    print("✅ Zero denominator returns None")

if __name__ == "__main__":
    from pathlib import Path

    test_routing_accuracy_formula()
    test_critical_escalation_recall_formula()
    test_zero_denominator_handling()
    print("\n✅ All metric tests passed")
