"""
Generate docs/dax-measures.md from the TMDL measure definitions.

The semantic model is saved as TMDL text (Power BI Project format), so the
measure catalogue can be rebuilt from source at any time and never drifts
from the model. Run:  python scripts/document_measures.py
"""

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "powerbi" / "PharmaProjectFinance.SemanticModel" / "definition" / "tables"
OUT = ROOT / "docs" / "dax-measures.md"


def parse(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    table = None
    i, desc = 0, []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("table "):
            table = ln[6:].strip().strip("'")
        if ln.startswith("\t///"):
            desc.append(ln.strip()[3:].strip())
        elif ln.startswith("\tmeasure "):
            head = ln[len("\tmeasure "):]
            name, _, expr = head.partition(" = ") if " = " in head else (head.rstrip(" ="), "", "")
            name = name.strip().strip("'")
            body = [expr.strip()] if expr.strip() else []
            props = {}
            i += 1
            while i < len(lines) and (lines[i].startswith("\t\t") or not lines[i].strip()):
                cur = lines[i]
                if cur.startswith("\t\t\t"):
                    body.append(cur[3:])
                elif cur.strip():
                    k, _, v = cur.strip().partition(": ")
                    props[k] = v
                i += 1
            yield {"table": table, "name": name, "description": " ".join(desc),
                   "expression": "\n".join(body).rstrip().replace("\t", "    "), "folder": props.get("displayFolder", "(root)"),
                   "format": props.get("formatString", "")}
            desc = []
            continue
        elif not ln.startswith("\t///"):
            desc = [] if ln.strip() else desc
        i += 1


measures = [m for f in sorted(TABLES.glob("*.tmdl")) for m in parse(f)]
by_folder = defaultdict(list)
for m in measures:
    by_folder[m["folder"] if m["table"] == "_Measures" else "7 What-if parameters"].append(m)

md = ["# DAX measure catalogue", "",
      f"_Generated from the TMDL source by `scripts/document_measures.py`: {len(measures)} measures._", "",
      "| Folder | Measures |", "|---|---|"]
for folder in sorted(by_folder):
    md.append(f"| {folder} | " + ", ".join(f"[{m['name']}](#{re.sub(r'[^a-z0-9 -]', '', m['name'].lower()).replace(' ', '-')})"
                                          for m in by_folder[folder]) + " |")
for folder in sorted(by_folder):
    md += ["", f"## {folder}", ""]
    for m in by_folder[folder]:
        md += [f"### {m['name']}", ""]
        if m["description"]:
            md += [m["description"], ""]
        md += ["```dax", f"{m['name']} =", m["expression"], "```", ""]
        if m["format"]:
            md += [f"Format: `{m['format']}`", ""]
OUT.write_text("\n".join(md), encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} ({len(measures)} measures)")
