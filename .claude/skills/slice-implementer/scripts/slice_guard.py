#!/usr/bin/env python3
"""Enforce a slice's contract: only allowlisted files change, frozen tests don't.

A slice brief (slices/S<nn>-<name>.md) contains one fenced block:

    ```slice
    id: S03
    depends_on: [S01]
    allow:
      - app/controllers/invoices_controller.rb
      - app/views/invoices/*.jbuilder
    frozen:
      - spec/requests/invoices_index_spec.rb
    done: bundle exec rspec spec/requests/invoices_index_spec.rb
    ```

Paths are relative to the repo root; globs use fnmatch rules. The slice's
report file (<slice dir>/<id>-REPORT.md) is always allowed.

Modes:
  validate <slice-file>             Check the contract parses and is consistent.
  check-diff <slice-file> <base>    Check every file changed since <base>
                                    (committed or not) is allowed and no
                                    frozen file changed. For the integrator.
  hook                              Claude Code PreToolUse hook. Reads the event
                                    JSON on stdin. Active only when a slice is
                                    set via $SLICE_FILE or a .slice-active file
                                    (containing the slice path) at the repo
                                    root; otherwise allows everything.

Exit codes: 0 ok, 1 violation (check-diff), 2 bad input / blocked (hook).
The hook fails closed: if a slice is active but its contract can't be read,
edits are denied.
"""
import fnmatch
import json
import os
import re
import subprocess
import sys

IGNORED = {".slice-active"}


def repo_root():
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if root:
        return os.path.realpath(root)
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return os.path.realpath(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return os.path.realpath(os.getcwd())


def parse_contract(path):
    """Parse the ```slice block. Raises ValueError with a readable message."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^```slice[ \t]*\n(.*?)^```", text, re.S | re.M)
    if not m:
        raise ValueError(f"{path}: no ```slice block found")
    contract, key = {}, None
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.+)$", line)
        if item:
            if key is None or not isinstance(contract.get(key), list):
                raise ValueError(f"{path}: list item outside a list: {line!r}")
            contract[key].append(item.group(1).strip().strip("'\""))
            continue
        kv = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not kv:
            raise ValueError(f"{path}: can't parse line: {line!r}")
        key, value = kv.group(1), kv.group(2).strip()
        if value == "":
            contract[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            contract[key] = [v.strip().strip("'\"") for v in inner.split(",") if v.strip()]
        else:
            contract[key] = value.strip("'\"")
    for required in ("id", "allow", "frozen", "done"):
        if required not in contract:
            raise ValueError(f"{path}: contract missing '{required}'")
    for list_key in ("allow", "frozen", "depends_on"):
        contract.setdefault(list_key, [])
        if not isinstance(contract[list_key], list):
            raise ValueError(f"{path}: '{list_key}' must be a list")
    if not contract["allow"]:
        raise ValueError(f"{path}: 'allow' is empty")
    if not isinstance(contract["done"], str) or not contract["done"]:
        raise ValueError(f"{path}: 'done' must be a single command")
    return contract


def report_path(slice_file, contract, root):
    rel_dir = os.path.relpath(os.path.dirname(os.path.realpath(slice_file)), root)
    return os.path.normpath(os.path.join(rel_dir, f"{contract['id']}-REPORT.md"))


def matches(rel, patterns):
    return any(fnmatch.fnmatch(rel, p) for p in patterns)


def verdict(rel, contract, report):
    """Return None if allowed, else the reason it's not."""
    rel = os.path.normpath(rel)
    if rel in IGNORED or rel == report:
        return None
    if matches(rel, contract["frozen"]):
        return (f"{rel} is a frozen test for slice {contract['id']}. Frozen tests "
                f"define done and may not be edited. If you believe the test is "
                f"wrong, stop and explain why in {report}.")
    if not matches(rel, contract["allow"]):
        return (f"{rel} is outside slice {contract['id']}'s allowlist "
                f"({', '.join(contract['allow'])}). Stay within the allowlist; if "
                f"the slice can't be done without this file, stop and say so in {report}.")
    return None


def active_slice(root):
    path = os.environ.get("SLICE_FILE")
    if not path:
        marker = os.path.join(root, ".slice-active")
        if os.path.exists(marker):
            with open(marker, encoding="utf-8") as f:
                path = f.read().strip()
    if not path:
        return None
    return path if os.path.isabs(path) else os.path.join(root, path)


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def cmd_hook():
    root = repo_root()
    slice_file = active_slice(root)
    if slice_file is None:
        sys.exit(0)  # not in slice mode
    try:
        event = json.load(sys.stdin)
        contract = parse_contract(slice_file)
    except (ValueError, OSError, json.JSONDecodeError) as e:
        deny(f"slice_guard: slice mode is active but the contract or hook input "
             f"can't be read ({e}); blocking edits to be safe.")
    tool_input = event.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        sys.exit(0)  # not a file edit (Bash is covered by check-diff)
    abs_target = os.path.realpath(target if os.path.isabs(target) else os.path.join(root, target))
    rel = os.path.relpath(abs_target, root)
    if rel.startswith(".."):
        deny(f"{target} is outside the repository; slices only change allowlisted files.")
    reason = verdict(rel, contract, report_path(slice_file, contract, root))
    if reason:
        deny(reason)
    sys.exit(0)


def changed_files(base):
    names = set()
    for args in (["git", "diff", "--name-only", f"{base}...HEAD"],
                 ["git", "diff", "--name-only", "HEAD"],
                 ["git", "ls-files", "--others", "--exclude-standard"]):
        out = subprocess.run(args, capture_output=True, text=True)
        if out.returncode != 0:
            print(f"git failed: {' '.join(args)}: {out.stderr.strip()}", file=sys.stderr)
            sys.exit(2)
        names.update(n for n in out.stdout.splitlines() if n)
    return sorted(names)


def cmd_check_diff(slice_file, base):
    root = repo_root()
    try:
        contract = parse_contract(slice_file)
    except (ValueError, OSError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    report = report_path(slice_file, contract, root)
    violations = []
    for rel in changed_files(base):
        reason = verdict(rel, contract, report)
        if reason:
            violations.append({"file": rel, "reason": reason})
    print(json.dumps({"slice": contract["id"], "ok": not violations,
                      "violations": violations}, indent=2))
    sys.exit(1 if violations else 0)


def cmd_validate(slice_file):
    try:
        contract = parse_contract(slice_file)
    except (ValueError, OSError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    # Frozen always wins over allow, so a broad allow glob around a frozen test
    # is fine; the same entry in both lists is a contradiction.
    both = sorted(set(contract["allow"]) & set(contract["frozen"]))
    if both:
        print(json.dumps({"ok": False, "error": f"listed as both allow and frozen: {both}"}))
        sys.exit(2)
    print(json.dumps({"ok": True, "contract": contract}))
    sys.exit(0)


def main():
    args = sys.argv[1:]
    if args == ["hook"]:
        cmd_hook()
    elif len(args) == 2 and args[0] == "validate":
        cmd_validate(args[1])
    elif len(args) == 3 and args[0] == "check-diff":
        cmd_check_diff(args[1], args[2])
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
