#!/bin/bash
# Check v2 baseline progress

echo "=== V2 BASELINE STATUS ==="
echo "Time: $(date)"
echo ""

if [ -f ".v2_baseline_checkpoint.json" ]; then
    COUNT=$(python3 -c "import json; print(len(json.load(open('.v2_baseline_checkpoint.json'))))")
    echo "Cases processed: $COUNT/375"
    PCT=$(python3 -c "print(f'{$COUNT/375*100:.1f}%')")
    echo "Progress: $PCT"
    echo ""

    # Estimate remaining time
    if [ "$COUNT" -gt 0 ]; then
        START=$(stat -f "%Sm" -t "%Y%m%d%H%M%S" .v2_baseline_checkpoint.json)
        NOW=$(date +%Y%m%d%H%M%S)
        ELAPSED=$((NOW - START))
        PER_CASE=$((ELAPSED / COUNT))
        REMAINING=$((PER_CASE * (375 - COUNT)))
        REMAINING_MINS=$((REMAINING / 60))
        echo "Estimated remaining: ${REMAINING_MINS} minutes"
    fi
else
    echo "No checkpoint found - run may not have started yet"
fi

echo ""
echo "Files:"
ls -la .v2_baseline_checkpoint.json benchmark/v2_baseline_results.jsonl 2>/dev/null || echo "  Still waiting..."
