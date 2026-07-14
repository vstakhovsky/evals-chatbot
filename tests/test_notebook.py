"""Notebook contract tests to ensure offline presentation behavior."""

import json
from pathlib import Path
import pytest

NOTEBOOK_PATH = (
    Path(__file__).resolve().parents[1]
    / "01_rag_baseline"
    / "faq_rag_chatbot.ipynb"
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
)

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Product Problem",
    "Data Lineage",
    "Benchmark Schema",
    "Family-Level Split Verification",
    "Label Status",
    "Limitations"
]


def test_notebook_is_offline_report() -> None:
    """Notebook must be an offline presentation report with no API calls."""
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    # Check for forbidden legacy content
    all_source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
    )

    violations = []
    for forbidden in FORBIDDEN_TEXT:
        if forbidden in all_source:
            violations.append(forbidden)

    if violations:
        pytest.fail(
            f"Offline notebook contains forbidden legacy content: {violations}"
        )

    # Check for required sections
    markdown_content = all_source
    missing_sections = []
    for section in REQUIRED_SECTIONS:
        if section not in markdown_content:
            missing_sections.append(section)

    if missing_sections:
        pytest.fail(f"Missing required sections: {missing_sections}")


def test_notebook_kernel_spec_is_generic() -> None:
    """Notebook should use generic python3 kernel, not local environment."""
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    kernelspec = notebook.get("metadata", {}).get("kernelspec", {})

    # Should use generic python3, not local environment name
    display_name = kernelspec.get("display_name", "")
    kernel_name = kernelspec.get("name", "")

    if kernel_name and "evals-chatbot" in kernel_name.lower():
        pytest.fail("Notebook uses local kernel instead of generic python3")

    if display_name and "evals-chatbot" in display_name.lower():
        pytest.fail("Notebook kernel display_name references local environment")


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


if __name__ == "__main__":
    # Run tests locally
    print("Running notebook contract tests...")
    test_notebook_is_offline_report()
    test_notebook_kernel_spec_is_generic()
    test_notebook_has_correct_structure()
    print("✅ All notebook tests passed")
