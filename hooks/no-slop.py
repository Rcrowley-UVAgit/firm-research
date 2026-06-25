#!/usr/bin/env python3
"""PostToolUse hook: warn when a freshly written text draft contains common
filler. Non-blocking; surfaces a message so the draft can be cleaned before it
is treated as done. Reads the hook JSON payload on stdin.
"""
import sys
import json
import os

TEXT_EXT = {".md", ".markdown", ".txt", ".rst"}
FILLER = [
    "it is important to note",
    "it's important to note",
    "it is worth noting",
    "needless to say",
    "in today's",
    "ever-evolving",
    "in conclusion,",
    "delve into",
    "a testament to",
]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    path = (payload.get("tool_input") or {}).get("file_path", "")
    if not path or os.path.splitext(path)[1].lower() not in TEXT_EXT:
        sys.exit(0)
    if not os.path.isfile(path):
        sys.exit(0)

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        sys.exit(0)

    problems = []
    low = text.lower()
    hits = sorted({p for p in FILLER if p in low})
    if hits:
        problems.append("filler phrases: " + "; ".join(hits))

    if problems:
        msg = (f"Draft check on {os.path.basename(path)}: "
               + " | ".join(problems)
               + ". Rewrite before treating this as final.")
        print(json.dumps({"systemMessage": msg}))
    sys.exit(0)


if __name__ == "__main__":
    main()
