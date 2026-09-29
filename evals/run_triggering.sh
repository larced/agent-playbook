#!/usr/bin/env bash
# Skill-triggering check: which skill does a one-turn headless run pick first?
# Usage: evals/run_triggering.sh [--model haiku] [--only-failures results.csv] [--out file.csv]
# Runs each case in a throwaway copy of the repo; no skill body executes past turn 1.
set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CASES="$REPO/evals/triggering.json"
MODEL=haiku
ONLY=""
OUT="$REPO/evals/triggering-results.csv"
WORK="${TRIGGER_WORKDIR:-${TMPDIR:-/tmp}/trigger-evals}"

while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --only-failures) ONLY="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

command -v claude >/dev/null || { echo "claude CLI not found" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 1; }

ids=$(jq -r '.[].id' "$CASES")
if [ -n "$ONLY" ]; then
  ids=$(awk -F, 'NR>1 && $4=="fail" {print $1}' "$ONLY")
fi

mkdir -p "$WORK/logs"
echo "id,expect,got,pass" > "$OUT"

for id in $ids; do
  prompt=$(jq -r --arg id "$id" '.[] | select(.id==$id) | .prompt' "$CASES")
  expect=$(jq -r --arg id "$id" '.[] | select(.id==$id) | .expect' "$CASES")

  copy="$WORK/repo"
  rm -rf "$copy" && cp -r "$REPO" "$copy" && rm -rf "$copy/evals"
  log="$WORK/logs/$MODEL-$id.jsonl"
  (cd "$copy" && timeout 180 claude -p "$prompt" --model "$MODEL" --max-turns 1 \
      --output-format stream-json --verbose > "$log" 2>&1)

  # First tool_use in the stream: its skill name if it's a Skill call, else none.
  got=$(jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")
               | if .name=="Skill" then (.input.skill // .input.command // "none") else "none" end' \
        "$log" 2>/dev/null | head -1)
  got="${got:-none}"
  got="${got#/}"

  pass=fail
  IFS='|' read -ra alts <<< "$expect"
  for a in "${alts[@]}"; do [ "$a" = "$got" ] && pass=pass; done

  echo "$id,$expect,$got,$pass" | tee -a "$OUT"
done

total=$(($(wc -l < "$OUT") - 1))
passed=$(tail -n +2 "$OUT" | grep -c ',pass$')
echo "model=$MODEL passed=$passed/$total"
