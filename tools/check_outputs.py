"""Check that every printed output in the lessons is a real run.

A lesson marks an output block like this:

    <!-- output: examples/gates.py table and -->
    ```text
    ...exactly what that command prints...
    ```

This script runs each command from the repository root and compares. With
--write it pastes the fresh output into the markdown instead. Stdlib only.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BLOCK = re.compile(r"(<!-- output: (.+?) -->\n```text\n)(.*?)(```)", re.S)


def run(command):
    result = subprocess.run([sys.executable, *command.split()], cwd=REPO_ROOT,
                            capture_output=True, text=True, check=True)
    return result.stdout.rstrip() + "\n"


def main():
    write = "--write" in sys.argv
    checked = failures = 0
    for markdown in sorted((REPO_ROOT / "lessons").glob("*.md")):
        text = markdown.read_text(encoding="utf-8")

        def replace(match):
            nonlocal checked, failures
            checked += 1
            fresh = run(match.group(2))
            if fresh != match.group(3) and not write:
                failures += 1
                print(f"{markdown.name}: stale output for `{match.group(2)}`")
            return match.group(1) + fresh + match.group(4)

        new = BLOCK.sub(replace, text)
        if write and new != text:
            markdown.write_text(new, encoding="utf-8")
    print(f"output blocks checked: {checked}, stale: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
