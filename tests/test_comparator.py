# tests/test_comparator.py
import pytest
import os
import yaml
from comparator import load_yaml_files, compare_element_names, compare_element_requirements

YAML_A = "tests/fixtures/a.yaml"
YAML_B = "tests/fixtures/b.yaml"


@pytest.fixture(autouse=True)
def create_fixtures():
    os.makedirs("tests/fixtures", exist_ok=True)
    with open(YAML_A, "w") as f:
        yaml.dump({
            "element1": {"name": "Password", "requirements": ["req1", "req2"]}
        }, f)
    with open(YAML_B, "w") as f:
        yaml.dump({
            "element1": {"name": "Network", "requirements": ["req1", "req3"]}
        }, f)


def test_load_yaml_files():
    d1, d2 = load_yaml_files(YAML_A, YAML_B)
    assert isinstance(d1, dict)
    assert isinstance(d2, dict)


def test_compare_element_names(tmp_path):
    out = compare_element_names(YAML_A, YAML_B, output_dir=str(tmp_path))
    assert os.path.exists(out)
    with open(out) as f:
        content = f.read()
    assert "Password" in content or "Network" in content


def test_compare_element_requirements(tmp_path):
    out = compare_element_requirements(YAML_A, YAML_B, output_dir=str(tmp_path))
    assert os.path.exists(out)
    with open(out) as f:
        content = f.read()
    assert "," in content or "NO DIFFERENCES" in content