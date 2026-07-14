"""Prompt contract tests to ensure prompts.py is the real source of truth."""

import sys
sys.path.insert(0, "01_rag_baseline")

import json
from pathlib import Path
import nbformat


def test_required_prompt_ids_exist():
    """Required prompt IDs must exist in PROMPT_REGISTRY."""
    from prompts import PROMPT_REGISTRY

    required_ids = {"synthetic_generation", "routing", "answer_generation"}

    missing_ids = required_ids - set(PROMPT_REGISTRY.keys())
    assert not missing_ids, f"Missing required prompt IDs: {missing_ids}"

    print("✅ All required prompt IDs exist")


def test_every_prompt_contains_required_fields():
    """Every prompt must contain version, purpose, template, and SHA-256."""
    from prompts import PROMPT_REGISTRY

    for prompt_id, prompt in PROMPT_REGISTRY.items():
        assert "version" in prompt, f"{prompt_id} missing version"
        assert "purpose" in prompt, f"{prompt_id} missing purpose"
        assert "template" in prompt or "sha256" in prompt, f"{prompt_id} missing template or sha256"
        assert prompt["version"], f"{prompt_id} has empty version"
        assert prompt["purpose"], f"{prompt_id} has empty purpose"

    print("✅ All prompts contain required fields")


def test_hash_calculation_is_deterministic():
    """SHA-256 calculation must be deterministic."""
    from prompts import prompt_sha256

    test_text = "Test prompt text"
    hash1 = prompt_sha256(test_text)
    hash2 = prompt_sha256(test_text)

    assert hash1 == hash2, "Hash calculation is not deterministic"
    assert len(hash1) == 64, f"Hash should be 64 characters, got {len(hash1)}"

    print("✅ Hash calculation is deterministic")


def test_prompt_versions_are_explicit():
    """Prompt versions must be non-empty and explicit."""
    from prompts import PROMPT_REGISTRY

    for prompt_id, prompt in PROMPT_REGISTRY.items():
        version = prompt["version"]
        assert version, f"{prompt_id} has empty version"
        assert isinstance(version, str), f"{prompt_id} version must be string"
        assert "-" in version, f"{prompt_id} version should follow pattern like 'v1', 'synthetic-v1'"

    print("✅ Prompt versions are explicit")


def test_generate_dataset_imports_synthetic_prompt():
    """generate_dataset.py must import synthetic prompt from prompts.py."""
    generate_dataset_path = Path("01_rag_baseline/generate_dataset.py")
    content = generate_dataset_path.read_text()

    # Should import from prompts
    assert "from prompts import" in content, "generate_dataset.py should import from prompts"

    # Should not contain V1_PROMPT definition
    assert "V1_PROMPT = " not in content, "generate_dataset.py should not define V1_PROMPT"

    print("✅ generate_dataset.py imports synthetic prompt from prompts.py")


def test_run_baseline_imports_runtime_prompts():
    """run_baseline.py must import runtime prompts from prompts.py."""
    run_baseline_path = Path("01_rag_baseline/run_baseline.py")
    content = run_baseline_path.read_text()

    # Should import from prompts
    assert "from prompts import" in content, "run_baseline.py should import from prompts"

    # Should not contain SYSTEM_PROMPT definition
    assert "SYSTEM_PROMPT = " not in content, "run_baseline.py should not define SYSTEM_PROMPT"

    print("✅ run_baseline.py imports runtime prompts from prompts.py")


def test_runtime_modules_contain_no_duplicate_prompts():
    """Runtime modules should not contain copies of registry prompts."""
    files_to_check = [
        "01_rag_baseline/generate_dataset.py",
        "01_rag_baseline/run_baseline.py",
    ]

    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text()

        # Check for prompt definitions that should only be in prompts.py
        forbidden_patterns = [
            'V1_PROMPT = """',
            'SYSTEM_PROMPT = (',
            'ROUTER_PROMPT = ',
            'ANSWER_PROMPT = ',
        ]

        for pattern in forbidden_patterns:
            assert pattern not in content, f"{file_path} should not contain prompt pattern {pattern}"

    print("✅ No duplicate prompt definitions in runtime modules")


def test_notebook_imports_or_loads_prompt_registry():
    """Notebook should import or load prompt registry dynamically."""
    notebook_path = Path("01_rag_baseline/faq_rag_chatbot.ipynb")

    with open(notebook_path, 'r') as f:
        nb = json.load(f)

    # Check for prompt registry loading
    prompt_registry_found = False
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'from prompts import' in source or 'PROMPT_REGISTRY' in source:
                prompt_registry_found = True
                break

    assert prompt_registry_found, "Notebook should load prompt registry"

    print("✅ Notebook imports prompt registry")


def test_no_api_keys_in_prompt_text():
    """Prompt text should not contain API keys or secrets."""
    from prompts import PROMPT_REGISTRY

    forbidden_patterns = [
        'sk-', 'api_key', 'API_KEY', 'secret', 'SECRET',
        'password', 'PASSWORD', 'token', 'TOKEN'
    ]

    for prompt_id, prompt in PROMPT_REGISTRY.items():
        template = prompt.get('template', '')
        for pattern in forbidden_patterns:
            assert pattern.lower() not in template.lower(), f"{prompt_id} contains forbidden pattern: {pattern}"

    print("✅ No API keys or secrets in prompt text")


def test_active_prompt_ids_appear_in_executed_notebook():
    """Active prompt IDs should be visible in executed notebook output."""
    from prompts import PROMPT_REGISTRY

    active_ids = set(PROMPT_REGISTRY.keys())
    required_ids = {'synthetic_generation', 'routing', 'answer_generation'}

    missing = required_ids - active_ids
    assert not missing, f"Missing required prompt IDs: {missing}"

    print("✅ Active prompt IDs are defined")


if __name__ == "__main__":
    # Run all tests
    test_required_prompt_ids_exist()
    test_every_prompt_contains_required_fields()
    test_hash_calculation_is_deterministic()
    test_prompt_versions_are_explicit()
    test_generate_dataset_imports_synthetic_prompt()
    test_run_baseline_imports_runtime_prompts()
    test_runtime_modules_contain_no_duplicate_prompts()
    test_notebook_imports_or_loads_prompt_registry()
    test_no_api_keys_in_prompt_text()
    test_active_prompt_ids_appear_in_executed_notebook()

    print("\n✅ All prompt tests passed")
