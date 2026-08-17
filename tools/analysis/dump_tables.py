"""Dump markdown tables of all RTL modules to file with UTF-8."""
import os
import json

workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(workspace, "docs", "hierarchy_data.json")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

def collect_modules(node, mod_dict):
    mod_name = node["module_name"]
    if mod_name not in mod_dict:
        mod_dict[mod_name] = {
            "ports": node["ports"],
            "params": node["parameters"]
        }
    for c in node["children"]:
        collect_modules(c, mod_dict)

all_mods = {}
for top in data:
    collect_modules(top, all_mods)

lines = []
lines.append(f"# RTL Module Interface Specification\n")
lines.append(f"Total Unique RTL Modules: {len(all_mods)}\n")
for mname, mdata in sorted(all_mods.items()):
    lines.append(f"### Module: `{mname}`")
    if mdata["params"]:
        lines.append("**Parameters:**")
        for p in mdata["params"]:
            lines.append(f"- `{p['name']}` ({p['type']})")
    else:
        lines.append("**Parameters:** *(None)*")
    lines.append("\n**Ports Table:**")
    lines.append("| Port | Direction | Type / Width |")
    lines.append("| :--- | :--- | :--- |")
    for p in mdata["ports"]:
        pdir = p["direction"]
        ptype = p["type"]
        lines.append(f"| `{p['name']}` | **{pdir}** | `{ptype}` |")
    lines.append("\n---\n")

out_docs_path = os.path.join(workspace, "docs", "rtl_summary_tables.md")
with open(out_docs_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Saved {out_docs_path} successfully.")
