#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../qlib-data"

export QLIB_PROVIDER_URI="$DATA_DIR"
export QLIB_REGION="cn"
export QLIB_INSTRUMENTS="sh510300"
export QLIB_START_TIME="2015-01-05"
export QLIB_END_TIME="2026-07-18"
export QLIB_TRAIN_END_TIME="2023-12-31"
export QLIB_TEST_START_TIME="2024-01-01"

python "$SCRIPT_DIR/alpha_feature_sets.py"
