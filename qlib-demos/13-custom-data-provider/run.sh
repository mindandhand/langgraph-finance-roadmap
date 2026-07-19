#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# This demo does not use qlib init; it demonstrates raw data validation and
# transformation before loading into qlib.
python "$SCRIPT_DIR/custom_data_provider.py"
