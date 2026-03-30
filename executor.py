# executor.py
import os
import subprocess
import json
import pandas as pd


KDE_TO_CONTROLS = {
    "Password":       ["C-0220", "C-0221"],
    "User Account":   ["C-0015", "C-0017"],
    "Network":        ["C-0044", "C-0046"],
    "Log":            ["C-0026"],
    "Container":      ["C-0009", "C-0013"],
    "Secret":         ["C-0012"],
    "RBAC":           ["C-0030", "C-0031"],
    "ServiceAccount": ["C-0034"],
}


def load_diff_files(name_diff: str, req_diff: str) -> tuple:
    """Load the two TEXT diff files from Task 2."""
    results = []
    for path in (name_diff, req_diff):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Diff file not found: {path}")
        with open(path) as f:
            results.append(f.read().strip())
    return results[0], results[1]


def determine_controls(name_diff_path: str, req_diff_path: str,
                       output_dir: str = "outputs") -> tuple:
    """Return controls TEXT file path and list of control IDs."""
    name_content, req_content = load_diff_files(name_diff_path, req_diff_path)

    no_diff = (
            "NO DIFFERENCES IN REGARDS TO ELEMENT NAMES" in name_content and
            "NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS" in req_content
    )

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "controls.txt")

    if no_diff:
        with open(out_path, "w") as f:
            f.write("NO DIFFERENCES FOUND")
        return out_path, []

    kde_names = set()
    for line in (name_content + "\n" + req_content).splitlines():
        for kde in KDE_TO_CONTROLS:
            if kde.lower() in line.lower():
                kde_names.add(kde)

    controls = []
    for kde in kde_names:
        controls.extend(KDE_TO_CONTROLS.get(kde, []))
    controls = sorted(set(controls))

    if not controls:
        controls = sorted({c for cs in KDE_TO_CONTROLS.values() for c in cs})

    with open(out_path, "w") as f:
        f.write("\n".join(controls))

    return out_path, controls


def run_kubescape(controls_path: str, yamls_dir: str = "project-yamls") -> pd.DataFrame:
    """Run Kubescape and return results as a DataFrame."""
    with open(controls_path) as f:
        content = f.read().strip()

    os.makedirs("outputs", exist_ok=True)

    if content == "NO DIFFERENCES FOUND":
        cmd = ["kubescape", "scan", yamls_dir,
               "--format", "json", "--output", "outputs/ks_results.json"]
    else:
        control_ids = [c.strip() for c in content.splitlines() if c.strip()]
        controls_arg = ",".join(control_ids)
        cmd = ["kubescape", "scan", "control", controls_arg,
               yamls_dir, "--format", "json", "--output", "outputs/ks_results.json"]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, capture_output=True, text=True)

    try:
        with open("outputs/ks_results.json") as f:
            data = json.load(f)

        rows = []
        for result_item in data.get("results", []):
            for control in result_item.get("controls", []):
                rows.append({
                    "FilePath":         result_item.get("resourceID", ""),
                    "Severity":         control.get("severity", {}).get("severity", ""),
                    "Control name":     control.get("name", ""),
                    "Failed resources": control.get("summary", {}).get("failedResources", 0),
                    "All Resources":    control.get("summary", {}).get("allResources", 0),
                    "Compliance score": control.get("summary", {}).get("complianceScore", 0),
                })
        return pd.DataFrame(rows)

    except Exception as e:
        print(f"Warning: could not parse Kubescape output: {e}")
        return pd.DataFrame(columns=[
            "FilePath", "Severity", "Control name",
            "Failed resources", "All Resources", "Compliance score"
        ])


def save_csv(df: pd.DataFrame, output_path: str = "outputs/kubescape_results.csv") -> str:
    """Save the Kubescape results DataFrame to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"CSV saved: {output_path}")
    return output_path