"""
tests/test_all.py
One test case per function — Task 1 (6), Task 2 (3), Task 3 (4).
All tests use only tmp_path / monkeypatching so they pass without
the real Gemma model, real PDFs, or Kubescape installed.
"""

import os
import json
import yaml
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# ─────────────────────────────────────────────────────────────────
# TASK 1 — extractor.py
# ─────────────────────────────────────────────────────────────────

from extractor import (
    load_documents,
    build_zero_shot_prompt,
    build_few_shot_prompt,
    build_chain_of_thought_prompt,
    run_llm_and_save_yaml,
    collect_llm_outputs,
)


# T1-1: load_documents — raises on missing file
def test_load_documents_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_documents(str(tmp_path / "ghost.pdf"), str(tmp_path / "ghost2.pdf"))


# T1-2: build_zero_shot_prompt — returns a non-empty string containing YAML hint
def test_build_zero_shot_prompt():
    result = build_zero_shot_prompt("Users must have unique passwords.")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "YAML" in result or "element" in result


# T1-3: build_few_shot_prompt — contains example block
def test_build_few_shot_prompt():
    result = build_few_shot_prompt("Logs must be retained for 90 days.")
    assert isinstance(result, str)
    assert "Example" in result or "example" in result


# T1-4: build_chain_of_thought_prompt — contains step instructions
def test_build_chain_of_thought_prompt():
    result = build_chain_of_thought_prompt("Accounts must be locked after 5 failed attempts.")
    assert isinstance(result, str)
    assert "Step" in result


# T1-5: run_llm_and_save_yaml — saves a YAML file and returns a dict
def test_run_llm_and_save_yaml(tmp_path):
    """Mock the tokenizer/model so no GPU or HuggingFace download needed."""
    mock_tokenizer = MagicMock()
    mock_tokenizer.return_value = {"input_ids": MagicMock()}
    mock_tokenizer.decode.return_value = (
        "element1:\n  name: Password\n  requirements:\n    - Must be 8 chars\n"
    )

    mock_model = MagicMock()
    mock_model.generate.return_value = [[0]]

    doc_text = "Passwords must be at least 8 characters."
    pdf_path = str(tmp_path / "cis-r1.pdf")
    out_dir = str(tmp_path / "yamls")

    result = run_llm_and_save_yaml(
        doc_text,
        pdf_path,
        build_zero_shot_prompt,
        "zero-shot",
        mock_tokenizer,
        mock_model,
        output_dir=out_dir,
    )

    assert isinstance(result, dict)
    yaml_files = os.listdir(out_dir)
    assert any(f.endswith(".yaml") for f in yaml_files)


# T1-6: collect_llm_outputs — writes TEXT file with required headers
def test_collect_llm_outputs(tmp_path):
    out_path = str(tmp_path / "outputs" / "llm_outputs.txt")
    entries = [
        {
            "llm_name": "google/gemma-3-1b-it",
            "prompt": "Test prompt",
            "prompt_type": "zero-shot",
            "output": "element1:\n  name: Password",
        }
    ]
    collect_llm_outputs(entries, output_path=out_path)

    assert os.path.exists(out_path)
    content = open(out_path).read()
    assert "*LLM Name*" in content
    assert "*Prompt Used*" in content
    assert "*Prompt Type*" in content
    assert "*LLM Output*" in content


# ─────────────────────────────────────────────────────────────────
# TASK 2 — comparator.py
# ─────────────────────────────────────────────────────────────────

from comparator import load_yaml_files, compare_element_names, compare_element_requirements

YAML_A = {
    "element1": {"name": "Password", "requirements": ["Must be 8 chars", "Must not be reused"]},
    "element2": {"name": "UserAccount", "requirements": ["Must be unique"]},
}

YAML_B = {
    "element1": {"name": "Password", "requirements": ["Must be 8 chars"]},
    "element2": {"name": "Log", "requirements": ["Must be retained 90 days"]},
}


def _write_yaml(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)


# T2-1: load_yaml_files — raises on missing YAML
def test_load_yaml_files_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_yaml_files(str(tmp_path / "a.yaml"), str(tmp_path / "b.yaml"))


# T2-2: compare_element_names — detects name differences
def test_compare_element_names(tmp_path):
    ya = tmp_path / "doc_a-zero-shot-kdes.yaml"
    yb = tmp_path / "doc_b-zero-shot-kdes.yaml"
    _write_yaml(ya, YAML_A)
    _write_yaml(yb, YAML_B)

    out = compare_element_names(str(ya), str(yb), output_dir=str(tmp_path / "out"))
    content = open(out).read()
    # "UserAccount" is in A but not B; "Log" is in B but not A
    assert "UserAccount" in content or "Log" in content


# T2-3: compare_element_requirements — correct tuple format
def test_compare_element_requirements(tmp_path):
    ya = tmp_path / "doc_a-zero-shot-kdes.yaml"
    yb = tmp_path / "doc_b-zero-shot-kdes.yaml"
    _write_yaml(ya, YAML_A)
    _write_yaml(yb, YAML_B)

    out = compare_element_requirements(str(ya), str(yb), output_dir=str(tmp_path / "out"))
    content = open(out).read()

    # Should NOT be the old bare "NAME,REQ" format — must include ABSENT-IN / PRESENT-IN
    if content.strip() != "NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS":
        lines = [l for l in content.strip().splitlines() if l]
        for line in lines:
            parts = line.split(",")
            assert len(parts) >= 4, f"Line missing tuple fields: {line}"
            assert "ABSENT-IN" in parts[1] or "PRESENT-IN" in parts[1], \
                f"Line missing ABSENT-IN/PRESENT-IN: {line}"


# ─────────────────────────────────────────────────────────────────
# TASK 3 — executor.py
# ─────────────────────────────────────────────────────────────────

from executor import load_diff_files, determine_controls, run_kubescape, save_csv


# T3-1: load_diff_files — raises on missing file
def test_load_diff_files_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_diff_files(str(tmp_path / "n.txt"), str(tmp_path / "r.txt"))


# T3-2: determine_controls — writes "NO DIFFERENCES FOUND" when no diffs
def test_determine_controls_no_diff(tmp_path):
    nd = tmp_path / "name_diff.txt"
    rd = tmp_path / "req_diff.txt"
    nd.write_text("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES")
    rd.write_text("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS")

    out_path, controls = determine_controls(str(nd), str(rd), output_dir=str(tmp_path / "out"))
    content = open(out_path).read()
    assert content.strip() == "NO DIFFERENCES FOUND"
    assert controls == []


# T3-3: run_kubescape — returns DataFrame (mock subprocess so no kubescape binary needed)
def test_run_kubescape_no_diff(tmp_path):
    controls_file = tmp_path / "controls.txt"
    controls_file.write_text("NO DIFFERENCES FOUND")

    ks_json = {
        "results": [
            {
                "resourceID": "path/to/deploy.yaml",
                "controls": [
                    {
                        "name": "Privileged container",
                        "severity": {"severity": "High"},
                        "summary": {
                            "failedResources": 1,
                            "allResources": 3,
                            "complianceScore": 66,
                        },
                    }
                ],
            }
        ]
    }

    out_dir = tmp_path / "outputs"
    out_dir.mkdir()
    ks_out = out_dir / "ks_results.json"

    def fake_run(cmd, **kwargs):
        ks_out.write_text(json.dumps(ks_json))

    with patch("executor.subprocess.run", side_effect=fake_run):
        with patch("executor.os.makedirs"):
            df = run_kubescape(str(controls_file), yamls_dir=str(tmp_path / "yamls"))

    assert isinstance(df, pd.DataFrame)


# T3-4: save_csv — writes CSV with required headers
def test_save_csv(tmp_path):
    df = pd.DataFrame([{
        "FilePath": "deploy.yaml",
        "Severity": "High",
        "Control name": "Privileged container",
        "Failed resources": 1,
        "All Resources": 3,
        "Compliance score": 66,
    }])
    out = str(tmp_path / "results.csv")
    path = save_csv(df, output_path=out)

    assert os.path.exists(path)
    import csv
    with open(path) as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
    required = ["FilePath", "Severity", "Control name", "Failed resources",
                "All Resources", "Compliance score"]
    for h in required:
        assert h in headers, f"Missing header: {h}"