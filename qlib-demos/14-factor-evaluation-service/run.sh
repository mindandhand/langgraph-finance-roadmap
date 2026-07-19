#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../qlib-data"

export QLIB_PROVIDER_URI="$DATA_DIR"
export QLIB_REGION="cn"
export QLIB_INSTRUMENTS="sh510300"
export QLIB_START_TIME="2015-01-05"
export QLIB_END_TIME="2026-07-18"

# Optional: write metrics to a JSON file
# OUTPUT="$SCRIPT_DIR/artifacts/metrics.json"

python "$SCRIPT_DIR/factor_evaluation_service.py" \
  --expression '$close / Ref($close, 20) - 1' \
  --label 'Ref($close, -5) / $close - 1'
  # --output "$OUTPUT"
