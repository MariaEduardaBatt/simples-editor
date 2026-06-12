import os
import re
import subprocess
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"


def gh(*args):
    token = os.environ.get("GH_TOKEN")
    env = {**os.environ, "GH_TOKEN": token} if token else os.environ
    result = subprocess.run(
        ["gh"] + list(args), capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"gh {' '.join(args)} failed: {result.stderr}")
        return None
    return result.stdout.strip()


def get_closed_issues():
    output = gh("issue", "list", "--state", "closed", "--limit", "100",
                "--json", "number,title,labels,closedAt")
    if output is None:
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def get_merged_prs():
    output = gh("pr", "list", "--state", "merged", "--limit", "100",
                "--json", "number,title,mergedAt")
    if output is None:
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def normalize_title(title):
    title = title.lower().strip()
    title = re.sub(r'^feat\s*', '', title)
    title = re.sub(r'^fix\s*', '', title)
    title = re.sub(r'^chore\s*', '', title)
    title = re.sub(r'^docs\s*', '', title)
    title = re.sub(r'^refactor\s*', '', title)
    title = re.sub(r'^test\s*', '', title)
    title = re.sub(r'^style\s*', '', title)
    title = re.sub(r'^ci\s*', '', title)
    title = re.sub(r'^build\s*', '', title)
    title = re.sub(r'^perf\s*', '', title)
    title = re.sub(r'\(.*?\)\s*', '', title)
    return title.strip()


def should_mark_done(progress_line, closed_items, merged_items):
    match = re.match(r'-\s*\[.\]\s*(.*)', progress_line)
    if not match:
        return False
    line_text = match.group(1).strip()
    norm_line = normalize_title(line_text)

    for item in closed_items:
        norm_item = normalize_title(item["title"])
        if norm_line == norm_item or norm_item in norm_line or norm_line in norm_item:
            return True

    for item in merged_items:
        norm_item = normalize_title(item["title"])
        if norm_line == norm_item or norm_item in norm_line or norm_line in norm_item:
            return True

    return False


def main():
    closed_issues = get_closed_issues()
    merged_prs = get_merged_prs()

    if not closed_issues and not merged_prs:
        print("No closed issues or merged PRs found. Skipping.")
        return

    lines = PROGRESS_PATH.read_text(encoding="utf-8").splitlines()
    updated = []
    changes = 0

    for line in lines:
        if re.match(r'-\s*\[ \]\s*', line):
            if should_mark_done(line, closed_issues, merged_prs):
                done_line = line.replace("[ ]", "[x]", 1)
                updated.append(done_line)
                changes += 1
                print(f"  [MARKED] {line.strip()}")
            else:
                updated.append(line)
        else:
            updated.append(line)

    if changes:
        PROGRESS_PATH.write_text("\n".join(updated) + "\n", encoding="utf-8")
        print(f"\n{changes} item(s) updated in PROGRESS.md")
    else:
        print("No changes to PROGRESS.md")


if __name__ == "__main__":
    main()
