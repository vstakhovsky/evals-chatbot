"""Notebook contract tests to ensure offline presentation behavior."""

import json
from pathlib import Path
import pytest

NOTEBOOK_PATH = (
    Path(__file__).resolve().parents[1]
    / "01_rag_baseline"
    / "faq_rag_chatbot.ipynb"
)

DRAFT_PATH = (
    Path(__file__).resolve().parents[1]
    / "01_rag_baseline"
    / "faq_rag_chatbot_draft.ipynb"
)

FORBIDDEN_TEXT = (
    "%pip",
    "OpenAI(",
    "load_dotenv",
    "OPENAI_API_KEY",
    "synthetic_queries.csv",
    "synthetic_rag_outputs.csv",
    "synthetic_eval_results.csv",
    "v2_baseline_results.jsonl",
    "validated benchmark",
    "frozen eval set",
    "150 synthetic queries",
    # Audit/legacy content
    "Executive Summary",
    "Product Problem",
    "Data Lineage",
    "Benchmark Schema",
    "Family-Level Split Verification",
    "Label Status",
    "Stage 02–04 Roadmap",
    "Reproduction Instructions",
)

REQUIRED_SECTIONS = [
    "Setup",
    "Load articles",
    "Embed all articles",
    "Retrieval",
    "Single-turn chat",
    "Try it",
    "Evaluate synthetic dataset",
    "LLM-as-a-Judge evaluation",
    "Metric correlations",
    "Conclusions"
]


def test_draft_notebook_exists() -> None:
    """Draft notebook should exist as archive."""
    assert DRAFT_PATH.exists(), "Draft notebook does not exist"


def test_notebook_is_offline_report() -> None:
    """Notebook must be an offline presentation report with no API calls."""
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    # Check for forbidden content
    all_source = "\n".join(
        "".join(cell.get("source", []))
        if isinstance(cell.get("source", []), list)
        else cell.get("source", "")
        for cell in notebook["cells"]
    )

    violations = []
    for forbidden in FORBIDDEN_TEXT:
        if forbidden in all_source:
            violations.append(forbidden)

    if violations:
        pytest.fail(
            f"Offline notebook contains forbidden content: {violations}"
        )

    # Check for required sections
    markdown_content = all_source
    missing_sections = []
    for section in REQUIRED_SECTIONS:
        if section not in markdown_content:
            missing_sections.append(section)

    if missing_sections:
        pytest.fail(f"Missing required sections: {missing_sections}")


def test_notebook_has_visible_outputs() -> None:
    """Notebook must have visible outputs for deterministic stages."""
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    code_cells_with_outputs = 0
    total_code_cells = 0

    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            total_code_cells += 1
            if cell.get("outputs") and len(cell.get("outputs", [])) > 0:
                code_cells_with_outputs += 1

    # At least some code cells should have outputs
    assert code_cells_with_outputs > 0, "No code cells have visible outputs"


def test_notebook_has_correct_structure() -> None:
    """Notebook must have required structure and no execution errors."""
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    # Must have cells
    assert len(notebook["cells"]) >= 20, "Notebook too small"

    # Must have both markdown and code cells
    cell_types = {c["cell_type"] for c in notebook["cells"]}
    assert "markdown" in cell_types, "Missing markdown cells"
    assert "code" in cell_types, "Missing code cells"

    # Check for error outputs in code cells
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    pytest.fail(
                        f"Cell {notebook['cells'].index(cell)} has error output: "
                        f"{output.get('ename', 'Unknown')}"
                    )


def test_notebook_sections_1_to_8_exist() -> None:
    """Notebook must contain sections 1 through 8."""
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    headings = "\n".join(
        "".join(cell.get("source", []))
        if isinstance(cell.get("source", []), list)
        else cell.get("source", "")
        for cell in notebook["cells"]
        if cell.get("cell_type") == "markdown"
    )

    for number in range(1, 9):
        found = (
            f"## {number}." in headings or
            f"## {number} " in headings
        )
        assert found, f"Section {number} not found"


if __name__ == "__main__":
    # Run tests locally
    print("Running notebook contract tests...")
    test_draft_notebook_exists()
    test_notebook_is_offline_report()
    test_notebook_has_visible_outputs()
    test_notebook_has_correct_structure()
    test_notebook_sections_1_to_8_exist()
    print("✅ All notebook tests passed")
