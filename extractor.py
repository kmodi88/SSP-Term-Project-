# extractor.py
import fitz  # PyMuPDF
import yaml
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "google/gemma-3-1b-it"


# ── Item 1: Load & validate documents ──────────────────────────
def load_documents(path1: str, path2: str) -> tuple:
    """Load and validate two PDF files. Returns their text content."""
    texts = []
    for path in (path1, path2):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        if not path.lower().endswith(".pdf"):
            raise ValueError(f"File is not a PDF: {path}")
        doc = fitz.open(path)
        if doc.page_count == 0:
            raise ValueError(f"PDF has no pages: {path}")
        text = "\n".join(page.get_text() for page in doc)
        if not text.strip():
            raise ValueError(f"PDF has no extractable text: {path}")
        texts.append(text)
    return texts[0], texts[1]


# ── Item 2: Zero-shot prompt ────────────────────────────────────
def build_zero_shot_prompt(doc_text: str) -> str:
    return (
        "You are a security analyst. Read the following security requirements "
        "document and identify all Key Data Elements (KDEs). For each KDE, "
        "list its name and the specific requirements that reference it. "
        "Return ONLY valid YAML in this exact format:\n"
        "element1:\n  name: <name>\n  requirements:\n    - <req1>\n    - <req2>\n\n"
        f"Document:\n{doc_text[:3000]}"
    )


# ── Item 3: Few-shot prompt ─────────────────────────────────────
def build_few_shot_prompt(doc_text: str) -> str:
    example = (
        "Example input: 'Passwords must be at least 8 characters. "
        "Passwords must not be reused within 12 months.'\n"
        "Example output:\n"
        "element1:\n  name: Password\n  requirements:\n"
        "    - Passwords must be at least 8 characters\n"
        "    - Passwords must not be reused within 12 months\n\n"
    )
    return (
            "You are a security analyst. Below is an example of identifying "
            "Key Data Elements (KDEs) from a security requirements document.\n\n"
            + example
            + "Now do the same for this document. Return ONLY valid YAML:\n\n"
              f"Document:\n{doc_text[:3000]}"
    )


# ── Item 4: Chain-of-thought prompt ────────────────────────────
def build_chain_of_thought_prompt(doc_text: str) -> str:
    return (
        "You are a security analyst. Follow these steps to identify Key Data "
        "Elements (KDEs) from a security requirements document:\n"
        "Step 1: Read the full document carefully.\n"
        "Step 2: Identify all distinct data entities mentioned (e.g., passwords, "
        "user accounts, logs).\n"
        "Step 3: For each entity, collect every requirement sentence that references it.\n"
        "Step 4: Format your findings as valid YAML only, like this:\n"
        "element1:\n  name: <name>\n  requirements:\n    - <req1>\n    - <req2>\n\n"
        f"Document:\n{doc_text[:3000]}"
    )


# ── Item 5: Run LLM and save YAML files ────────────────────────
def run_llm_and_save_yaml(
        doc_text: str,
        pdf_path: str,
        prompt_func,
        prompt_type: str,
        tokenizer,
        model,
        output_dir: str = "yamls"
) -> dict:
    prompt = prompt_func(doc_text)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=512)
    raw_output = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Try to parse YAML from output
    kde_dict = {}
    try:
        if "element1:" in raw_output:
            yaml_part = "element1:" + raw_output.split("element1:")[1]
            kde_dict = yaml.safe_load(yaml_part)
        if not isinstance(kde_dict, dict):
            kde_dict = {}
    except Exception:
        kde_dict = {}

    if not kde_dict:
        kde_dict = {"element1": {"name": "Unknown", "requirements": [raw_output[:200]]}}

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    os.makedirs(output_dir, exist_ok=True)
    yaml_filename = os.path.join(output_dir, f"{base_name}-{prompt_type}-kdes.yaml")
    with open(yaml_filename, "w") as f:
        yaml.dump(kde_dict, f, default_flow_style=False)

    return kde_dict


# ── Item 6: Collect all LLM outputs to TEXT file ───────────────
def collect_llm_outputs(results: list, output_path: str = "outputs/llm_outputs.txt"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        for entry in results:
            f.write(f"*LLM Name*\n{entry['llm_name']}\n\n")
            f.write(f"*Prompt Used*\n{entry['prompt']}\n\n")
            f.write(f"*Prompt Type*\n{entry['prompt_type']}\n\n")
            f.write(f"*LLM Output*\n{entry['output']}\n\n")
            f.write("=" * 60 + "\n\n")


# ── Main runner for Task 1 ──────────────────────────────────────
def run_task1(pdf1: str, pdf2: str):
    print(f"Loading model {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)
    model.eval()

    text1, text2 = load_documents(pdf1, pdf2)

    prompt_funcs = {
        "zero-shot":        build_zero_shot_prompt,
        "few-shot":         build_few_shot_prompt,
        "chain-of-thought": build_chain_of_thought_prompt,
    }

    all_results = []
    for pdf_path, doc_text in [(pdf1, text1), (pdf2, text2)]:
        for ptype, pfunc in prompt_funcs.items():
            print(f"  Running {ptype} on {pdf_path}...")
            prompt_str = pfunc(doc_text)
            kde_dict = run_llm_and_save_yaml(
                doc_text, pdf_path, pfunc, ptype, tokenizer, model
            )
            all_results.append({
                "llm_name":   MODEL_NAME,
                "prompt":     prompt_str,
                "prompt_type": ptype,
                "output":     str(kde_dict),
            })

    collect_llm_outputs(all_results)
    print("Task 1 complete.")
    return text1, text2