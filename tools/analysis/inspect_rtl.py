r"""
Script to inspect all RTL modules in D:\NCKH using pyslang.
Extracts:
- Module Name
- Source File
- Parameters (name, type, default)
- Ports (name, direction, data type, bit width)
- Sub-instances instantiated
- Full hierarchy tree
"""

import os
import pyslang
import json

workspace = r"D:\NCKH"

rtl_files = [
    os.path.join(workspace, r"rtl\top\top_module.v"),
    os.path.join(workspace, r"rtl\mac\secure_mac.v"),
    os.path.join(workspace, r"rtl\cpu\riscv_cpu.sv"),
    os.path.join(workspace, r"rtl\cpu\imem.sv"),
    os.path.join(workspace, r"rtl\cpu\dmem.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_if_id.sv"),
    os.path.join(workspace, r"rtl\cpu\instruction_decoder.sv"),
    os.path.join(workspace, r"rtl\cpu\control_unit.sv"),
    os.path.join(workspace, r"rtl\cpu\regfile.sv"),
    os.path.join(workspace, r"rtl\cpu\branch_cmp.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_id_ex.sv"),
    os.path.join(workspace, r"rtl\cpu\alu.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_ex_mem.sv"),
    os.path.join(workspace, r"rtl\cpu\pipe_mem_wb.sv"),
    os.path.join(workspace, r"rtl\cpu\hazard_unit.sv"),
    os.path.join(workspace, r"rtl\top\alu_top.sv"),
]

comp = pyslang.Compilation()
for f in rtl_files:
    if os.path.exists(f):
        comp.addSyntaxTree(pyslang.SyntaxTree.fromFile(f))

root = comp.getRoot()

def get_inst_data(inst):
    name = inst.name
    mod_name = inst.definition.name if hasattr(inst, "definition") and inst.definition else "unknown"
    
    ports = []
    if hasattr(inst, "body") and inst.body and hasattr(inst.body, "portList"):
        for p in inst.body.portList:
            pdir = str(getattr(p, "direction", "")).replace("ArgumentDirection.", "")
            ptype = str(getattr(p, "type", ""))
            ports.append({"name": p.name, "direction": pdir, "type": ptype})
            
    params = []
    if hasattr(inst, "body") and inst.body:
        for m in inst.body:
            if str(m.kind) == "SymbolKind.Parameter":
                params.append({"name": m.name, "type": str(getattr(m, "type", ""))})
                
    children = []
    if hasattr(inst, "body") and inst.body:
        for m in inst.body:
            if str(m.kind) == "SymbolKind.Instance":
                children.append(get_inst_data(m))
                
    return {
        "instance_name": name,
        "module_name": mod_name,
        "parameters": params,
        "ports": ports,
        "children": children
    }

print("=" * 80)
print("TOP LEVEL INSTANCE HIERARCHIES")
print("=" * 80)

hierarchy_data = []
for top_inst in root.topInstances:
    data = get_inst_data(top_inst)
    hierarchy_data.append(data)

def print_tree(node, indent=0):
    prefix = "  " * indent
    inst_name = node["instance_name"]
    mod_name = node["module_name"]
    num_ports = len(node["ports"])
    num_params = len(node["parameters"])
    print(f"{prefix}+-- {inst_name} ({mod_name}) [Ports: {num_ports}, Params: {num_params}]")
    for child in node["children"]:
        print_tree(child, indent + 1)

for h in hierarchy_data:
    print_tree(h)
    print()

# Save JSON representation in docs/
docs_dir = os.path.join(workspace, "docs")
os.makedirs(docs_dir, exist_ok=True)
with open(os.path.join(docs_dir, "hierarchy_data.json"), "w", encoding="utf-8") as f:
    json.dump(hierarchy_data, f, indent=2)

print(f"Saved {os.path.join(docs_dir, 'hierarchy_data.json')} successfully.")
