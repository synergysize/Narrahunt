# CCU AUTO-REFACTOR SCRIPT FOR NARRAHUNT PHASE 2
# BEFORE EXECUTING, READ /home/computeruse/.anthropic/ALWAYSREAD.txt AND FOLLOW EVERY RULE IN IT EXACTLY.

import os
import shutil
import re

from collections import defaultdict

src_dir = "/home/computeruse/.anthropic/narrahunt_phase2/src/"
modules_dir = os.path.join(src_dir, "modules")
os.makedirs(modules_dir, exist_ok=True)

def extract_utils(content):
    """Extract utility functions into modules if used in multiple files"""
    utils = []
    for match in re.finditer(r'^\s*def (\w+)\(', content, re.MULTILINE):
        func_name = match.group(1)
        if func_name.startswith("get_") or func_name.startswith("is_") or func_name in ("load_json", "save_json"):
            block = extract_function_block(content, func_name)
            if block:
                utils.append((func_name, block))
    return utils

def extract_function_block(content, name):
    """Extract function code block by name"""
    lines = content.splitlines()
    start, end = None, None
    for i, line in enumerate(lines):
        if re.match(rf'^\s*def {name}\(', line):
            start = i
            indent = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                if lines[j].strip() == "":
                    continue
                if len(lines[j]) - len(lines[j].lstrip()) <= indent and not lines[j].startswith(" " * (indent + 1)):
                    end = j
                    break
            break
    if start is not None:
        return "\n".join(lines[start:end]) if end else "\n".join(lines[start:])
    return None

def remove_unused_imports(content):
    """Remove imports that aren't used in the file"""
    lines = content.splitlines()
    used_names = set(re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', content))
    cleaned = []
    for line in lines:
        if line.strip().startswith(("import ", "from ")):
            import_name = re.findall(r'import\s+([A-Za-z0-9_\.]+)', line)
            from_name = re.findall(r'from\s+([A-Za-z0-9_\.]+)', line)
            check = (import_name or from_name)[0].split(".")[0]
            if check not in used_names:
                continue  # remove
        cleaned.append(line)
    return "\n".join(cleaned)

# Track utilities across files
util_registry = defaultdict(list)

for filename in os.listdir(src_dir):
    if not filename.endswith(".py"):
        continue
    path = os.path.join(src_dir, filename)

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup original
    shutil.copy(path, path + ".bak")

    # Phase 1: extract and track utility functions
    utils = extract_utils(content)
    for name, block in utils:
        util_registry[name].append((filename, block))

# Write common utilities to modules/utils.py
written_utils = {}
with open(os.path.join(modules_dir, "utils.py"), "w", encoding='utf-8') as out:
    out.write("# Common extracted utilities\n\n")
    for name, entries in util_registry.items():
        # Only write shared utilities
        if len(entries) > 1 and name not in written_utils:
            out.write(entries[0][1] + "\n\n")
            written_utils[name] = True

# Phase 2: clean and refactor each file
for filename in os.listdir(src_dir):
    if not filename.endswith(".py"):
        continue
    path = os.path.join(src_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove in-file utility defs now moved to utils
    for name in written_utils:
        content = re.sub(rf'\n?def {name}\(.*?\n(?:\s+.*\n)*', '', content, flags=re.MULTILINE)

    # Remove unused imports
    content = remove_unused_imports(content)

    # Add utils import if any extracted were used
    if any(name in content for name in written_utils):
        content = f"from modules.utils import {', '.join(written_utils)}\n\n" + content

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("✅ Code refactor complete. See /src/modules/utils.py and *.bak for backups.")