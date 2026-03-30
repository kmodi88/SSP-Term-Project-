# tests/test_extractor.py
import pytest
import os
import yaml
from extractor import (
    load_documents,
    build_zero_shot_prompt,
    build_few_shot_prompt,
    build_chain_of_thought_prompt,
    collect_llm_outputs,
)

SAMPLE_PDF = "pdfs/cis-r1.pdf"


def test_load_documents():
    t1, t2 = load_documents(SAMPLE_PDF, SAMPLE_PDF)
    assert isinstance(t1, str) and len(t1) > 0
    assert isinstance(t2, str) and len(t2) > 0


def test_zero_shot_prompt():
    p = build_zero_shot_prompt("Sample text about passwords.")
    assert isinstance(p, str) and len(p) > 0


def test_few_shot_prompt():
    p = build_few_shot_prompt("Sample text about user accounts.")
    assert isinstance(p, str) and "Example" in p


def test_chain_of_thought_prompt():
    p = build_chain_of_thought_prompt("Sample text about network security.")
    assert isinstance(p, str) and "Step" in p


def test_collect_llm_outputs(tmp_path):
    out = str(tmp_path / "test_out.txt")
    collect_llm_outputs([{
        "llm_name":    "TestLLM",
        "prompt":      "test prompt",
        "prompt_type": "zero-shot",
        "output":      "test output"
    }], output_path=out)
    assert os.path.exists(out)
    with open(out) as f:
        content = f.read()
    assert "*LLM Name*" in content
    assert "*Prompt Used*" in content
    assert "*Prompt Type*" in content
    assert "*LLM Output*" in content