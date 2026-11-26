#!/usr/bin/env python3
"""Count, for each item, the issues in which readers said "known", "new" or "the summary is wrong".

Usage: python3 -I tally.py OWNER/REPO OUT.json      (needs the `gh` command and GH_TOKEN)

An issue counts for an item when its form names the item (the "Item" field) or its title starts with
the item's id in square brackets, and it carries one of the labels below. Closed issues still count,
unless they are labelled `invalid`.
"""
import json
import re
import subprocess
import sys

KINDS = {"verdict:known": "known", "verdict:new": "new", "correction": "correction"}


def issues(repo):
    page = 1
    while True:
        out = subprocess.run(
            ["gh", "api", "repos/%s/issues?state=all&per_page=100&page=%d" % (repo, page)],
            check=True, capture_output=True, text=True).stdout
        batch = json.loads(out)
        if not batch:
            return
        for issue in batch:
            if "pull_request" not in issue:
                yield issue
        page += 1


def item_of(issue):
    m = re.search(r"###\s*Item\s+([AB]\d{2})\b", issue.get("body") or "")
    if m:
        return m.group(1)
    m = re.match(r"\s*\[([AB]\d{2})\]", issue.get("title") or "")
    return m.group(1) if m else None


def main(repo, out):
    tally = {}
    for issue in issues(repo):
        labels = {label["name"] for label in issue.get("labels", [])}
        item = item_of(issue)
        if item is None or "invalid" in labels:
            continue
        for label, kind in KINDS.items():
            if label in labels:
                tally.setdefault(item, {}).setdefault(kind, 0)
                tally[item][kind] += 1
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(tally, handle, indent=1, sort_keys=True)
    print("items with responses:", len(tally))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
