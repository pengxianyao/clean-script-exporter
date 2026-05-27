#!/bin/bash

# once.sh — Run one implementation session (human-in-loop version of the Ralph loop)
# Usage: ./once.sh

set -e

# Gather all open issue files
ISSUES=$(cat issues/*.md 2>/dev/null | head -c 50000)
if [ -z "$ISSUES" ]; then
  echo "No issue files found in /issues/. Create some first with /prd-to-issues."
  exit 1
fi

# Grab recent git context
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null || echo "No git history yet")

# Load the implement prompt
IMPLEMENT_PROMPT=$(cat .claude/skills/implement.md)

# Build the full prompt
FULL_PROMPT="Local issue files from /issues/ are provided below.

$IMPLEMENT_PROMPT

---

ISSUES:
$ISSUES

RECENT COMMITS:
$RECENT_COMMITS"

# Run Claude
claude --permission-mode acceptEdits "$FULL_PROMPT"
