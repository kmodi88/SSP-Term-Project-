# main.py
import sys
import os
from extractor import run_task1
from comparator import compare_element_names, compare_element_requirements
from executor import determine_controls, run_kubescape, save_csv

INPUTS = [
    ("pdfs/cis-r1.pdf", "pdfs/cis-r1.pdf"),
    ("pdfs/cis-r1.pdf", "pdfs/cis-r2.pdf"),
    ("pdfs/cis-r1.pdf", "pdfs/cis-r3.pdf"),
    ("pdfs/cis-r1.pdf", "pdfs/cis-r4.pdf"),
    ("pdfs/cis-r2.pdf", "pdfs/cis-r2.pdf"),
    ("pdfs/cis-r2.pdf", "pdfs/cis-r3.pdf"),
    ("pdfs/cis-r2.pdf", "pdfs/cis-r4.pdf"),
    ("pdfs/cis-r3.pdf", "pdfs/cis-r3.pdf"),
    ("pdfs/cis-r3.pdf", "pdfs/cis-r4.pdf"),
]


def run_pair(pdf1: str, pdf2: str):
    print(f"\n{'='*60}")
    print(f"Processing: {pdf1}  +  {pdf2}")
    print('='*60)

    # Task 1
    run_task1(pdf1, pdf2)

    # Task 2 - use zero-shot YAML files
    base1 = os.path.splitext(os.path.basename(pdf1))[0]
    base2 = os.path.splitext(os.path.basename(pdf2))[0]
    yaml1 = f"yamls/{base1}-zero-shot-kdes.yaml"
    yaml2 = f"yamls/{base2}-zero-shot-kdes.yaml"

    name_diff = compare_element_names(yaml1, yaml2)
    req_diff  = compare_element_requirements(yaml1, yaml2)

    # Task 3
    controls_path, _ = determine_controls(name_diff, req_diff)
    df = run_kubescape(controls_path)
    csv_out = f"outputs/{base1}_vs_{base2}_results.csv"
    save_csv(df, csv_out)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Run single pair: python main.py pdfs/cis-r1.pdf pdfs/cis-r2.pdf
        run_pair(sys.argv[1], sys.argv[2])
    else:
        # Run all 9 input combinations
        for pdf1, pdf2 in INPUTS:
            run_pair(pdf1, pdf2)