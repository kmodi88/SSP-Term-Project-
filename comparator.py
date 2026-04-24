# comparator.py
import yaml
import os


def load_yaml_files(yaml1: str, yaml2: str) -> tuple:
    """Load and validate two YAML files."""
    result = []
    for path in (yaml1, yaml2):
        if not os.path.exists(path):
            raise FileNotFoundError(f"YAML not found: {path}")
        with open(path) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"YAML did not parse to a dict: {path}")
        result.append(data)
    return result[0], result[1]


def compare_element_names(yaml1: str, yaml2: str, output_dir: str = "outputs") -> str:
    """Write TEXT file of differing KDE names between two YAMLs."""
    data1, data2 = load_yaml_files(yaml1, yaml2)

    names1 = {v.get("name") for v in data1.values() if isinstance(v, dict) and v.get("name")}
    names2 = {v.get("name") for v in data2.values() if isinstance(v, dict) and v.get("name")}

    diff = names1.symmetric_difference(names2)

    os.makedirs(output_dir, exist_ok=True)
    base1 = os.path.splitext(os.path.basename(yaml1))[0]
    base2 = os.path.splitext(os.path.basename(yaml2))[0]
    out_path = os.path.join(output_dir, f"{base1}_vs_{base2}_name_diff.txt")

    with open(out_path, "w") as f:
        if diff:
            f.write("\n".join(sorted(diff)))
        else:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES")

    return out_path


def compare_element_requirements(yaml1: str, yaml2: str, output_dir: str = "outputs") -> str:
    """Write TEXT file of differing KDE requirements between two YAMLs.

    Output format per rubric:
      NAME,ABSENT-IN-<FILE>,PRESENT-IN-<FILE>,NA      # KDE only in one file
      NAME,ABSENT-IN-<FILE>,PRESENT-IN-<FILE>,REQ     # req only in one file
    """
    data1, data2 = load_yaml_files(yaml1, yaml2)

    base1 = os.path.splitext(os.path.basename(yaml1))[0]
    base2 = os.path.splitext(os.path.basename(yaml2))[0]

    def req_map(data):
        m = {}
        for v in data.values():
            if isinstance(v, dict) and v.get("name"):
                m[v["name"]] = set(v.get("requirements") or [])
        return m

    map1, map2 = req_map(data1), req_map(data2)
    all_names = set(map1) | set(map2)

    diffs = []
    for name in sorted(all_names):
        in1 = name in map1
        in2 = name in map2

        # KDE present in one file but not the other
        if in1 and not in2:
            diffs.append(f"{name},ABSENT-IN-{base2},PRESENT-IN-{base1},NA")
            continue
        if in2 and not in1:
            diffs.append(f"{name},ABSENT-IN-{base1},PRESENT-IN-{base2},NA")
            continue

        # KDE present in both — compare requirements
        reqs1 = map1.get(name, set())
        reqs2 = map2.get(name, set())
        for req in sorted(reqs1 - reqs2):
            diffs.append(f"{name},ABSENT-IN-{base2},PRESENT-IN-{base1},{req}")
        for req in sorted(reqs2 - reqs1):
            diffs.append(f"{name},ABSENT-IN-{base1},PRESENT-IN-{base2},{req}")

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{base1}_vs_{base2}_req_diff.txt")

    with open(out_path, "w") as f:
        if diffs:
            f.write("\n".join(diffs))
        else:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS")

    return out_path