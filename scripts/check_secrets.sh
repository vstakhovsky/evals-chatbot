#!/bin/bash
set -euo pipefail

# Secret patterns to scan for
PATTERNS=(
  'sk-[A-Za-z0-9_-]{16,}'
  'api_key\s*=\s*["'"'"'][^"'"'"']{10,}["'"'"']'
  'Bearer [A-Za-z0-9._-]{20,}'
)

# Files to scan
TRACKED_FILES=$(git ls-files | grep -v '\.md$')
NOTEBOOK="01_rag_baseline/faq_rag_chatbot.ipynb"

echo "🔍 Scanning for secrets..."
echo ""

FOUND=0

# Scan tracked files (excluding markdown)
for pattern in "${PATTERNS[@]}"; do
  if echo "$TRACKED_FILES" | xargs grep -nE "$pattern" 2>/dev/null; then
    FOUND=1
  fi
done

# Scan notebook specifically (including outputs)
if [ -f "$NOTEBOOK" ]; then
  for pattern in "${PATTERNS[@]}"; do
    if grep -nE "$pattern" "$NOTEBOOK" 2>/dev/null; then
      FOUND=1
    fi
  done
fi

echo ""

if [ $FOUND -eq 1 ]; then
  echo "❌ SECRETS DETECTED - Do not commit!"
  exit 1
else
  echo "✅ No secrets found"
  exit 0
fi
