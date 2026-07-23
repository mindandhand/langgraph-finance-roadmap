#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../qlib-data"

export QLIB_PROVIDER_URI="$DATA_DIR"
export QLIB_REGION="cn"
source "$SCRIPT_DIR/../qlib_env.sh"
export QLIB_START_TIME="2015-01-05"
export QLIB_END_TIME="2026-07-18"

# Optional overrides:
# export QLIB_SCORE_EXPR='$close / Ref($close, 20) - 1'
# export QLIB_LABEL_EXPR='Ref($close, -2) / Ref($close, -1) - 1'
# export QLIB_TOPK=1
# export QLIB_COST_RATE=0.001

python "$SCRIPT_DIR/strategy_and_backtest.py"
