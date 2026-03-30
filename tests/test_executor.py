# tests/test_executor.py
import pytest
import os
import pandas as pd
from executor import load_diff_files, determine_controls, save_csv

NAME_DIFF = "tests/fixtures/name_diff.txt"
REQ_DIFF  = "tests/fixtures/req_diff.txt"


@pytest.fixture(autouse=True)
def create_fixtures():
    os.makedirs("tests/fixtures", exist_ok=True)
    with open(NAME_DIFF, "w") as f:
        f.write("Password\nNetwork")
    with open(REQ_DIFF, "w") as f:
        f.write("Password,Passwords must be rotated every 90 days")


def test_load_diff_files():
    n, r = load_diff_files(NAME_DIFF, REQ_DIFF)
    assert isinstance(n, str)
    assert isinstance(r, str)


def test_determine_controls(tmp_path):
    out, controls = determine_controls(NAME_DIFF, REQ_DIFF, output_dir=str(tmp_path))
    assert os.path.exists(out)
    assert isinstance(controls, list)


def test_save_csv(tmp_path):
    df = pd.DataFrame([{
        "FilePath":         "test.yaml",
        "Severity":         "High",
        "Control name":     "C-0001",
        "Failed resources": 1,
        "All Resources":    2,
        "Compliance score": 50
    }])
    out = str(tmp_path / "test.csv")
    save_csv(df, out)
    assert os.path.exists(out)