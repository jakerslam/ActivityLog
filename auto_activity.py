#!/usr/bin/env python3
"""
auto_activity.py
Append a small, legitimate change to a file and push to GitHub with a probability
(70% default) on weekdays. Safe checks for repo dir, only commits when we actually change a file.
"""

import os
import subprocess
import sys
from datetime import datetime
import random

# CONFIG — edit these
REPO_DIR = "/path/to/your/repo"        # << change this to your cloned repo path
FILENAME = "activity_log.txt"          # file to append to (in repo root)
PROBABILITY = 0.7                      # 70% chance
DRY_RUN = False                        # set True to test without pushing

# small phrases to make each commit slightly different / believable
NOTES = [
    "refactor notes",
    "small doc tweak",
    "daily log entry",
    "update dependencies list",
    "tiny formatting fix",
    "add sample output",
    "note about tests",
]

def run(cmd, cwd=None, capture=False):
    return subprocess.run(cmd, cwd=cwd, check=False, text=True,
                          stdout=(subprocess.PIPE if capture else None),
                          stderr=(subprocess.PIPE if capture else None))

def main():
    # ensure repo exists
    if not os.path.isdir(REPO_DIR):
        print(f"ERROR: REPO_DIR not found: {REPO_DIR}", file=sys.stderr)
        sys.exit(2)

    # check weekday: Monday=0 .. Sunday=6
    weekday = datetime.now().weekday()
    if weekday >= 5:
        print("Not a weekday (Sat/Sun). Exiting.")
        return

    r = random.random()
    print(f"Random roll: {r:.3f} (need < {PROBABILITY})")
    if r >= PROBABILITY:
        print("Skipping commit this run (rolled above probability).")
        return

    # Prepare file content
    ts = datetime.now().isoformat(timespec='seconds')
    note = random.choice(NOTES)
    line = f"{ts} — {note}\n"

    file_path = os.path.join(REPO_DIR, FILENAME)
    # ensure file directory exists (repo root assumed)
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print("ERROR writing file:", e, file=sys.stderr)
        sys.exit(3)

    # git add/commit/push
    try:
        # git status to ensure repo is okay
        res = run(["git", "status", "--porcelain"], cwd=REPO_DIR, capture=True)
        if res.returncode != 0:
            print("git status failed:", res.stderr or res.stdout, file=sys.stderr)
            sys.exit(4)

        # stage the file
        res = run(["git", "add", FILENAME], cwd=REPO_DIR, capture=True)
        if res.returncode != 0:
            print("git add failed:", res.stderr or res.stdout, file=sys.stderr)
            sys.exit(5)

        commit_msg = f"Automated activity: {ts} — {note}"
        if DRY_RUN:
            print("[DRY RUN] Would commit with message:", commit_msg)
            return

        res = run(["git", "commit", "-m", commit_msg], cwd=REPO_DIR, capture=True)
        # if nothing to commit, git returns non-zero and message in stdout
        if res.returncode != 0:
            print("git commit returned non-zero. Output:")
            print(res.stdout or res.stderr)
            # nothing to commit? then exit without pushing
            return

        # push
        res = run(["git", "push"], cwd=REPO_DIR, capture=True)
        if res.returncode != 0:
            print("git push failed:", res.stderr or res.stdout, file=sys.stderr)
            sys.exit(6)

        print("Success: committed and pushed:", commit_msg)

    except Exception as e:
        print("ERROR during git operations:", e, file=sys.stderr)
        sys.exit(7)

if __name__ == "__main__":
    main()
