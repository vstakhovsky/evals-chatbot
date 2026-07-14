"""Dataset validation tests."""
import json
import hashlib
from pathlib import Path

def test_canonical_benchmark_exists():
    """Test that canonical benchmark exists and is valid."""
    canonical_path = Path("01_rag_baseline/benchmark/cases.jsonl")
    assert canonical_path.exists(), "Canonical benchmark must exist"

    with open(canonical_path, 'r') as f:
        cases = [json.loads(line) for line in f if line.strip()]

    assert len(cases) == 355, f"Expected 355 cases, got {len(cases)}"
    print("✅ Canonical benchmark: 355 cases")

def test_canonical_benchmark_hash():
    """Test that canonical benchmark has stable hash."""
    canonical_path = Path("01_rag_baseline/benchmark/cases.jsonl")
    hash_path = Path("01_rag_baseline/benchmark/cases/hash.sha256")

    if hash_path.exists():
        with open(hash_path, 'r') as f:
            recorded_hash = f.read().strip()

        with open(canonical_path, 'r') as f:
            content = f.read()
            current_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        assert recorded_hash == current_hash, "Benchmark hash must be stable"
        print(f"✅ Benchmark hash stable: {recorded_hash[:16]}...")

def test_no_duplicate_case_ids():
    """Test that all case_ids are unique."""
    canonical_path = Path("01_rag_baseline/benchmark/cases.jsonl")

    with open(canonical_path, 'r') as f:
        case_ids = []
        for line in f:
            if line.strip():
                case = json.loads(line)
                case_ids.append(case['case_id'])

    assert len(case_ids) == len(set(case_ids)), "All case_ids must be unique"
    print("✅ No duplicate case_ids")

def test_all_cases_have_lineage():
    """Test that all cases have source_collection and source_case_id."""
    canonical_path = Path("01_rag_baseline/benchmark/cases.jsonl")

    with open(canonical_path, 'r') as f:
        for line in f:
            if line.strip():
                case = json.loads(line)
                assert 'source_collection' in case, f"Missing source_collection in {case['case_id']}"
                assert 'source_case_id' in case, f"Missing source_case_id in {case['case_id']}"

    print("✅ All cases have lineage")

if __name__ == "__main__":
    test_canonical_benchmark_exists()
    test_canonical_benchmark_hash()
    test_no_duplicate_case_ids()
    test_all_cases_have_lineage()
    print("\n✅ All dataset tests passed")
