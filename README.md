# Security Requirements Change Detector

## Team Members
- Krish Modi — kjm0092@auburn.edu
- Ty Mullinax — tyb0042@auburn.edu

## LLM Used for Task 1
google/gemma-3-1b-it (via Hugging Face Transformers)

## Project Structure
```
project/
├── extractor.py       # Task 1 - PDF loading, prompts, LLM, YAML output
├── comparator.py      # Task 2 - YAML diffing
├── executor.py        # Task 3 - Kubescape control mapping and execution
├── main.py            # Runs all 9 input combinations
├── PROMPT.md          # All prompts used
├── requirements.txt   # All dependencies with versions
├── pdfs/              # Input PDF files
├── yamls/             # YAML output from Task 1
├── outputs/           # TEXT and CSV outputs
├── project-yamls/     # Unzipped Kubernetes YAML files for Kubescape
└── tests/             # All test cases
```

## How to Run

### Setup
```bash
py -m venv comp5700-venv
comp5700-venv\Scripts\activate
pip install -r requirements.txt
```

### Run a single pair
```bash
python main.py pdfs/cis-r1.pdf pdfs/cis-r2.pdf
```

### Run all 9 input combinations
```bash
python main.py
```

### Run tests
```bash
pytest tests/ -v
```