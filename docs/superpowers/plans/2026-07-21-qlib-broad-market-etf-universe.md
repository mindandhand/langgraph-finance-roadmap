# Qlib Broad-Market ETF Universe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the bundled Qlib provider and all demo defaults from one ETF to five broad-market ETFs with correct per-instrument history, reproducible generation, and cross-sectional demo output.

**Architecture:** Keep `download_to_qlib.py` as the provider builder, but separate instrument selection, frame validation, union-calendar construction, provider writing, validation, and atomic publication into focused functions. Build the complete provider in a sibling temporary directory, verify it, then swap it into place; all demo launchers use the same five-instrument environment string while retaining caller overrides.

**Tech Stack:** Python 3.10, pandas, NumPy, AkShare, Microsoft Qlib 0.9.7, `unittest`, Bash, Git.

## 2026-07-22 Execution Deviation

The user approved an AkShare Sina ETF-history fallback after EastMoney was unreachable during an earlier generation attempt. EastMoney remains primary. Sina is called with the validated exchange-qualified Qlib symbol, provides OHLCV but neither `amount` nor an adjustment selector, and is stored exactly as returned with an explicit price-semantics warning. Core required fields are `open`, `close`, `high`, `low`, `volume`, and `factor`; `amount` is optional and is never synthesized. Provider generation and validation must therefore require exactly the fields present for each frame—six files for Sina-backed frames, seven when the primary source supplies real amount. This decision supersedes later steps that unconditionally require amount, seven binaries, or guaranteed qfq semantics from Sina. The bundled provider committed by Task 4 was subsequently generated successfully from the EastMoney primary source for all five ETFs, so every committed instrument has all seven feature files, including real source-provided `amount`.

---

## File Map

- Modify `qlib-demos/download_to_qlib.py`: define the default ETF universe and build validated multi-instrument Qlib providers.
- Create `qlib-demos/tests/test_download_to_qlib.py`: unit tests for universe selection, union calendars, metadata, binary layout, and publication rollback.
- Modify `qlib-demos/tests/test_qlib_expressions.py`: require multiple instruments in the real `03` output while preserving the existing binary-header regression.
- Create `qlib-demos/qlib_env.sh`: own the shared five-instrument default while retaining caller overrides.
- Modify `qlib-demos/01-environment-and-data/run.sh` through `qlib-demos/14-factor-evaluation-service/run.sh`: source the shared Qlib environment.
- Modify `qlib-demos/README.md`: document the bundled ETF universe and regeneration behavior.
- Modify `qlib-demos/03-qlib-expressions/README.md`: explain that the demo now displays a real ETF cross-section while expression `Rank` remains time-series rolling rank.
- Replace `qlib-demos/qlib-data/calendars/day.txt`, `qlib-demos/qlib-data/instruments/all.txt`, and `qlib-demos/qlib-data/features/*/*.day.bin`: regenerated five-instrument provider.

## Task 0: Checkpoint the Existing Qlib 03 Repair

The worktree already contains the previous verified repair: `Rank(feature, 20)`, corrected Rank documentation, the binary index-header fix, repaired `sh510300` files, and regression tests. Preserve it as a separate commit before starting the multi-ETF feature.

**Files:**
- Modify: `qlib-demos/03-qlib-expressions/README.md`
- Modify: `qlib-demos/03-qlib-expressions/qlib_expressions.py`
- Modify: `qlib-demos/download_to_qlib.py`
- Modify: `qlib-demos/qlib-data/features/sh510300/*.day.bin`
- Create: `qlib-demos/tests/test_qlib_expressions.py`

- [ ] **Step 1: Verify the existing regression suite and demo**

Run:

```bash
python -m unittest qlib-demos/tests/test_qlib_expressions.py -v
./qlib-demos/03-qlib-expressions/run.sh
git diff --check
```

Expected: two tests pass, `03` prints populated rows and the `rolling_mom20_rank` column, and `git diff --check` prints nothing.

- [ ] **Step 2: Commit only the existing repair**

```bash
git add \
  qlib-demos/03-qlib-expressions/README.md \
  qlib-demos/03-qlib-expressions/qlib_expressions.py \
  qlib-demos/download_to_qlib.py \
  qlib-demos/qlib-data/features/sh510300 \
  qlib-demos/tests/test_qlib_expressions.py
git commit -m "fix: repair qlib expression demo data"
```

Expected: the design and plan documents are not included in this commit; the working tree contains no remaining changes from the `03` repair.

## Task 1: Define and Test the Multi-ETF Provider Model

**Files:**
- Modify: `qlib-demos/download_to_qlib.py`
- Create: `qlib-demos/tests/test_download_to_qlib.py`

- [ ] **Step 1: Write failing tests for the default universe and union calendar**

Create `qlib-demos/tests/test_download_to_qlib.py` with:

```python
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "qlib-demos"))

from download_to_qlib import (
    DEFAULT_INSTRUMENTS,
    build_calendar,
    write_features,
    write_instruments,
)


class MultiInstrumentProviderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.calendar_a = pd.to_datetime(["2024-01-01", "2024-01-02"])
        self.calendar_b = pd.to_datetime(["2024-01-02", "2024-01-03"])
        self.frames = {
            "sh510050": pd.DataFrame(
                {"close": np.array([10.0, 11.0], dtype=np.float32)},
                index=self.calendar_a,
            ),
            "sh588000": pd.DataFrame(
                {"close": np.array([20.0, 21.0], dtype=np.float32)},
                index=self.calendar_b,
            ),
        }

    def test_default_universe_contains_five_broad_market_etfs(self) -> None:
        self.assertEqual(
            ["sh510050", "sh510300", "sh510500", "sz159915", "sh588000"],
            [item.qlib_symbol for item in DEFAULT_INSTRUMENTS],
        )

    def test_build_calendar_returns_sorted_union(self) -> None:
        calendar = build_calendar(self.frames)
        pd.testing.assert_index_equal(
            pd.DatetimeIndex(calendar),
            pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        )

    def test_metadata_and_feature_headers_keep_individual_ranges(self) -> None:
        calendar = build_calendar(self.frames)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_instruments(self.frames, output)
            for qlib_symbol, frame in self.frames.items():
                write_features(frame, qlib_symbol, calendar, output)

            metadata = (output / "instruments/all.txt").read_text().splitlines()
            second_values = np.fromfile(
                output / "features/sh588000/close.day.bin", dtype="<f4"
            )

        self.assertEqual(
            [
                "sh510050\t2024-01-01\t2024-01-02",
                "sh588000\t2024-01-02\t2024-01-03",
            ],
            metadata,
        )
        np.testing.assert_array_equal(
            np.array([1.0, 20.0, 21.0], dtype=np.float32), second_values
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
python -m unittest qlib-demos/tests/test_download_to_qlib.py -v
```

Expected: import failure for `DEFAULT_INSTRUMENTS` or `build_calendar`, proving the new multi-instrument contract does not exist yet.

- [ ] **Step 3: Add the instrument model and pure provider helpers**

In `qlib-demos/download_to_qlib.py`, replace the single-symbol constants with:

```python
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class InstrumentSpec:
    source_symbol: str
    qlib_symbol: str
    name: str


DEFAULT_INSTRUMENTS = (
    InstrumentSpec("510050", "sh510050", "上证50 ETF"),
    InstrumentSpec("510300", "sh510300", "沪深300 ETF"),
    InstrumentSpec("510500", "sh510500", "中证500 ETF"),
    InstrumentSpec("159915", "sz159915", "创业板 ETF"),
    InstrumentSpec("588000", "sh588000", "科创50 ETF"),
)
```

Replace `write_instruments` and add `build_calendar`:

```python
def build_calendar(frames: Mapping[str, pd.DataFrame]) -> pd.DatetimeIndex:
    if not frames:
        raise ValueError("at least one instrument is required")
    dates = pd.DatetimeIndex([])
    for frame in frames.values():
        dates = dates.union(pd.DatetimeIndex(frame.index))
    return dates.sort_values().unique()


def write_instruments(frames: Mapping[str, pd.DataFrame], out_dir: Path) -> None:
    path = out_dir / "instruments" / "all.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for qlib_symbol in sorted(frames):
        index = pd.DatetimeIndex(frames[qlib_symbol].index)
        lines.append(
            f"{qlib_symbol}\t{index[0]:%Y-%m-%d}\t{index[-1]:%Y-%m-%d}"
        )
    path.write_text("\n".join(lines) + "\n")
    print(f"[instruments] {len(lines)} instruments → {path}")
```

Keep `write_features` responsible for exactly one instrument. Its existing `np.hstack([start_pos, arr]).astype("<f4")` header format remains unchanged.

- [ ] **Step 4: Run the focused tests**

Run:

```bash
python -m unittest qlib-demos/tests/test_download_to_qlib.py -v
```

Expected: three tests pass.

- [ ] **Step 5: Commit the provider data model**

```bash
git add qlib-demos/download_to_qlib.py qlib-demos/tests/test_download_to_qlib.py
git commit -m "feat: model multi-etf qlib providers"
```

## Task 2: Validate Downloads and Publish Providers Safely

**Files:**
- Modify: `qlib-demos/download_to_qlib.py`
- Modify: `qlib-demos/tests/test_download_to_qlib.py`

- [ ] **Step 1: Add failing tests for validation, full provider writing, and rollback**

Extend `test_download_to_qlib.py` imports:

```python
from download_to_qlib import (
    DEFAULT_INSTRUMENTS,
    build_calendar,
    publish_provider,
    validate_frame,
    validate_provider,
    write_features,
    write_instruments,
    write_provider,
)
```

Add these tests:

```python
    def test_validate_frame_rejects_missing_required_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "sh510050.*volume"):
            validate_frame(
                self.frames["sh510050"],
                InstrumentSpec("510050", "sh510050", "上证50 ETF"),
            )

    def test_write_provider_creates_union_calendar_and_both_instruments(self) -> None:
        complete_frames = {
            symbol: pd.DataFrame(
                {
                    field: np.array([1.0, 2.0], dtype=np.float32)
                    for field in FEATURES
                },
                index=frame.index,
            )
            for symbol, frame in self.frames.items()
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_provider(complete_frames, output)
            calendar = (output / "calendars/day.txt").read_text().splitlines()

        self.assertEqual(["2024-01-01", "2024-01-02", "2024-01-03"], calendar)

    def test_validate_provider_accepts_complete_staged_data(self) -> None:
        complete_frames = {
            symbol: pd.DataFrame(
                {
                    field: np.array([1.0, 2.0], dtype=np.float32)
                    for field in FEATURES
                },
                index=frame.index,
            )
            for symbol, frame in self.frames.items()
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_provider(complete_frames, output)
            validate_provider(output, complete_frames)

    def test_publish_provider_restores_existing_target_when_swap_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "qlib-data"
            staging = root / "staging"
            target.mkdir()
            staging.mkdir()
            (target / "marker.txt").write_text("old")
            (staging / "marker.txt").write_text("new")

            def fail_staging_swap(source: Path, destination: Path) -> None:
                if source == staging:
                    raise OSError("swap failed")
                source.replace(destination)

            with mock.patch(
                "download_to_qlib._replace_path", side_effect=fail_staging_swap
            ):
                with self.assertRaisesRegex(OSError, "swap failed"):
                    publish_provider(staging, target)

            self.assertEqual("old", (target / "marker.txt").read_text())
```

Also add `from unittest import mock` and import `FEATURES` and `InstrumentSpec` from `download_to_qlib` at the top of the test module.

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python -m unittest qlib-demos/tests/test_download_to_qlib.py -v
```

Expected: import failures for `validate_frame`, `write_provider`, or `publish_provider`.

- [ ] **Step 3: Implement validation and complete provider writing**

Add to `download_to_qlib.py`:

```python
REQUIRED_FIELDS = ("open", "close", "high", "low", "volume", "amount", "factor")


def validate_frame(frame: pd.DataFrame, spec: InstrumentSpec) -> None:
    if frame.empty:
        raise ValueError(f"{spec.qlib_symbol}: download returned no rows")
    missing = [field for field in REQUIRED_FIELDS if field not in frame.columns]
    if missing:
        raise ValueError(
            f"{spec.qlib_symbol}: missing required fields: {', '.join(missing)}"
        )
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError(f"{spec.qlib_symbol}: index must be DatetimeIndex")
    if frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError(f"{spec.qlib_symbol}: dates must be sorted and unique")


def write_provider(frames: Mapping[str, pd.DataFrame], out_dir: Path) -> None:
    calendar = build_calendar(frames)
    write_calendar(calendar, out_dir)
    write_instruments(frames, out_dir)
    for qlib_symbol, frame in sorted(frames.items()):
        write_features(frame, qlib_symbol, calendar, out_dir)


def validate_provider(out_dir: Path, frames: Mapping[str, pd.DataFrame]) -> None:
    calendar = (out_dir / "calendars/day.txt").read_text().splitlines()
    metadata = (out_dir / "instruments/all.txt").read_text().splitlines()
    metadata_symbols = {line.split("\t", 1)[0] for line in metadata}
    if metadata_symbols != set(frames):
        raise ValueError("provider instrument metadata does not match downloaded frames")
    for qlib_symbol, frame in frames.items():
        start = frame.index[0].strftime("%Y-%m-%d")
        expected_start_index = calendar.index(start)
        feature_dir = out_dir / "features" / qlib_symbol
        for field in REQUIRED_FIELDS:
            path = feature_dir / f"{field}.day.bin"
            values = np.fromfile(path, dtype="<f4")
            if len(values) < 2 or int(values[0]) != expected_start_index:
                raise ValueError(f"invalid Qlib feature file: {path}")
```

- [ ] **Step 4: Implement safe provider publication**

Add imports and the publication helper:

```python
import shutil


def _replace_path(source: Path, target: Path) -> None:
    source.replace(target)


def publish_provider(staging: Path, target: Path) -> None:
    backup = target.with_name(f".{target.name}.backup")
    if backup.exists():
        shutil.rmtree(backup)
    if target.exists():
        _replace_path(target, backup)
    try:
        _replace_path(staging, target)
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup.exists():
            _replace_path(backup, target)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup)
```

- [ ] **Step 5: Extend CLI selection and batch download**

Make `--symbol` and `--qlib-symbol` default to `None`. Add:

```python
def selected_instruments(args: argparse.Namespace) -> tuple[InstrumentSpec, ...]:
    if bool(args.symbol) != bool(args.qlib_symbol):
        raise ValueError("--symbol and --qlib-symbol must be provided together")
    if args.symbol:
        return (InstrumentSpec(args.symbol, args.qlib_symbol, args.qlib_symbol),)
    return DEFAULT_INSTRUMENTS


def download_all(
    specs: tuple[InstrumentSpec, ...], start: str, end: str, adjust: str
) -> dict[str, pd.DataFrame]:
    frames = {}
    for spec in specs:
        try:
            frame = download(spec.source_symbol, start, end, adjust)
            validate_frame(frame, spec)
        except Exception as error:
            raise RuntimeError(
                f"failed to download {spec.qlib_symbol} ({spec.source_symbol})"
            ) from error
        frames[spec.qlib_symbol] = frame
    return frames
```

Rewrite `main()` so it downloads and validates everything before touching the target, writes into `tempfile.TemporaryDirectory(dir=out_dir.parent)`, calls `write_provider` and `validate_provider` on the staged directory, and only then calls `publish_provider`.

- [ ] **Step 6: Run tests and CLI help**

Run:

```bash
python -m unittest qlib-demos/tests/test_download_to_qlib.py -v
python qlib-demos/download_to_qlib.py --help
```

Expected: all provider tests pass; help describes five default ETFs and paired single-symbol overrides.

- [ ] **Step 7: Commit safe batch generation**

```bash
git add qlib-demos/download_to_qlib.py qlib-demos/tests/test_download_to_qlib.py
git commit -m "feat: build qlib providers atomically"
```

## Task 3: Make Every Demo Use the Broad-Market Universe

**Files:**
- Modify: `qlib-demos/01-environment-and-data/run.sh`
- Modify: `qlib-demos/02-qlib-data-api/run.sh`
- Modify: `qlib-demos/03-qlib-expressions/run.sh`
- Modify: `qlib-demos/04-data-handler-and-dataset/run.sh`
- Modify: `qlib-demos/05-labels-and-time-splits/run.sh`
- Modify: `qlib-demos/06-factor-evaluation/run.sh`
- Modify: `qlib-demos/07-model-training-baseline/run.sh`
- Modify: `qlib-demos/08-recorder-and-experiment/run.sh`
- Modify: `qlib-demos/09-strategy-and-backtest/run.sh`
- Modify: `qlib-demos/10-config-driven-alpha-workflow/run.sh`
- Modify: `qlib-demos/11-alpha158-alpha360-feature-sets/run.sh`
- Modify: `qlib-demos/12-native-backtest-architecture/run.sh`
- Modify: `qlib-demos/13-custom-data-provider/run.sh`
- Modify: `qlib-demos/14-factor-evaluation-service/run.sh`
- Create: `qlib-demos/qlib_env.sh`
- Modify: `qlib-demos/tests/test_qlib_expressions.py`
- Modify: `qlib-demos/tests/test_download_to_qlib.py`
- Modify: `qlib-demos/README.md`
- Modify: `qlib-demos/03-qlib-expressions/README.md`

- [ ] **Step 1: Write a failing test for the shared launcher environment**

Add to `test_download_to_qlib.py`:

```python
    def test_shared_shell_environment_exports_default_universe(self) -> None:
        result = subprocess.run(
            [
                "bash",
                "-c",
                'source qlib-demos/qlib_env.sh; printf "%s" "$QLIB_INSTRUMENTS"',
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            "sh510050,sh510300,sh510500,sz159915,sh588000", result.stdout
        )
```

Add `import subprocess` to the test module.

- [ ] **Step 2: Run the integration test to verify it fails**

Run:

```bash
python -m unittest \
  qlib-demos.tests.test_download_to_qlib.MultiInstrumentProviderTest.test_shared_shell_environment_exports_default_universe \
  -v
```

Expected: FAIL because `qlib-demos/qlib_env.sh` does not exist.

- [ ] **Step 3: Create the shared environment and update all launchers**

Create `qlib-demos/qlib_env.sh`:

```bash
#!/usr/bin/env bash

QLIB_DEFAULT_INSTRUMENTS="sh510050,sh510300,sh510500,sz159915,sh588000"
export QLIB_INSTRUMENTS="${QLIB_INSTRUMENTS:-$QLIB_DEFAULT_INSTRUMENTS}"
```

In every `qlib-demos/*/run.sh`, replace the hard-coded `export QLIB_INSTRUMENTS="sh510300"` with:

```bash
source "$SCRIPT_DIR/../qlib_env.sh"
```

This supplies five defaults but preserves an explicit caller override.

- [ ] **Step 4: Update documentation**

Add a “内置宽基 ETF 数据” section to `qlib-demos/README.md` containing the five-code table from the design, the command:

```bash
python qlib-demos/download_to_qlib.py
```

and these constraints:

- the calendar is the union of instrument trading dates;
- each instrument keeps its actual listing range;
- bundled ETFs are teaching data, not a production universe.

Update `03-qlib-expressions/README.md` to say its output contains a five-ETF cross-section. Keep the existing statement that `Rank(feature, N)` is a per-instrument rolling percentile; do not call it cross-sectional rank.

- [ ] **Step 5: Check shell syntax and expected defaults**

Run:

```bash
bash -n qlib-demos/*/run.sh
rg -n 'source .*qlib_env\.sh' qlib-demos/*/run.sh
python -m unittest \
  qlib-demos.tests.test_download_to_qlib.MultiInstrumentProviderTest.test_shared_shell_environment_exports_default_universe \
  -v
```

Expected: Bash syntax succeeds, all 14 launchers source `qlib_env.sh`, and the focused shell-environment test passes.

- [ ] **Step 6: Commit launcher and documentation changes**

```bash
git add qlib-demos/qlib_env.sh qlib-demos/*/run.sh qlib-demos/README.md \
  qlib-demos/03-qlib-expressions/README.md \
  qlib-demos/tests/test_download_to_qlib.py
git commit -m "feat: use broad-market etfs in qlib demos"
```

## Task 4: Regenerate and Validate the Bundled Provider

**Files:**
- Replace: `qlib-demos/qlib-data/calendars/day.txt`
- Replace: `qlib-demos/qlib-data/instruments/all.txt`
- Create: `qlib-demos/qlib-data/features/sh510050/*.day.bin`
- Replace: `qlib-demos/qlib-data/features/sh510300/*.day.bin`
- Create: `qlib-demos/qlib-data/features/sh510500/*.day.bin`
- Create: `qlib-demos/qlib-data/features/sz159915/*.day.bin`
- Create: `qlib-demos/qlib-data/features/sh588000/*.day.bin`
- Modify: `qlib-demos/tests/test_download_to_qlib.py`

- [ ] **Step 1: Add a bundled-provider consistency test**

Add to `test_download_to_qlib.py`:

```python
    def test_bundled_provider_contains_default_universe(self) -> None:
        provider = ROOT / "qlib-demos/qlib-data"
        metadata = (provider / "instruments/all.txt").read_text().splitlines()
        metadata_symbols = [line.split("\t", 1)[0] for line in metadata]
        feature_symbols = sorted(
            path.name for path in (provider / "features").iterdir() if path.is_dir()
        )

        expected = sorted(item.qlib_symbol for item in DEFAULT_INSTRUMENTS)
        self.assertEqual(expected, sorted(metadata_symbols))
        self.assertEqual(expected, feature_symbols)
```

In `test_qlib_expressions.py`, add after the existing output assertions:

```python
        self.assertIn("sh510050", result.stdout)
        self.assertIn("sh510300", result.stdout)
        self.assertIn("sh510500", result.stdout)
        self.assertIn("sz159915", result.stdout)
        self.assertIn("sh588000", result.stdout)
```

- [ ] **Step 2: Run it to verify it fails**

Run:

```bash
python -m unittest \
  qlib-demos.tests.test_download_to_qlib.MultiInstrumentProviderTest.test_bundled_provider_contains_default_universe \
  -v
```

Expected: FAIL because only `sh510300` exists.

- [ ] **Step 3: Generate the real provider**

Run from the repository root:

```bash
python qlib-demos/download_to_qlib.py --start 20100104 --end 20260720
```

Expected: all five ETF downloads succeed before publication. EastMoney-backed frames have seven feature files when real amount is returned; Sina-backed frames have six and omit `amount.day.bin`.

- [ ] **Step 4: Validate provider metadata and binary headers**

Run:

```bash
python - <<'PY'
from pathlib import Path
import numpy as np

provider = Path("qlib-demos/qlib-data")
calendar = (provider / "calendars/day.txt").read_text().splitlines()
metadata = (provider / "instruments/all.txt").read_text().splitlines()
assert len(metadata) == 5, metadata
for line in metadata:
    symbol, start, end = line.split("\t")
    start_index = calendar.index(start)
    for path in sorted((provider / "features" / symbol).glob("*.day.bin")):
        values = np.fromfile(path, dtype="<f4")
        assert int(values[0]) == start_index, (path, values[0], start_index)
        assert len(values) > 2, path
print(f"calendar={len(calendar)} instruments={len(metadata)} binary_headers=ok")
PY
```

Expected: `instruments=5` and `binary_headers=ok`.

- [ ] **Step 5: Run all focused tests**

Run:

```bash
python -m unittest discover -s qlib-demos/tests -v
```

Expected: every provider and expression test passes, including all five instrument names in `03` output.

- [ ] **Step 6: Commit regenerated provider data**

```bash
git add qlib-demos/qlib-data \
  qlib-demos/tests/test_download_to_qlib.py \
  qlib-demos/tests/test_qlib_expressions.py
git commit -m "data: add broad-market etf qlib provider"
```

## Task 5: End-to-End Demo Verification

**Files:**
- Verify only.

- [ ] **Step 1: Verify source and shell syntax**

Run:

```bash
python -m py_compile \
  qlib-demos/download_to_qlib.py \
  qlib-demos/03-qlib-expressions/qlib_expressions.py \
  qlib-demos/tests/test_download_to_qlib.py \
  qlib-demos/tests/test_qlib_expressions.py
bash -n qlib-demos/*/run.sh
git diff --check
```

Expected: all commands exit zero with no syntax or whitespace errors.

- [ ] **Step 2: Run the complete Qlib test suite**

Run:

```bash
python -m unittest discover -s qlib-demos/tests -v
```

Expected: all tests pass with no failures or errors.

- [ ] **Step 3: Run representative demos**

Run:

```bash
./qlib-demos/01-environment-and-data/run.sh
./qlib-demos/02-qlib-data-api/run.sh
./qlib-demos/03-qlib-expressions/run.sh
./qlib-demos/06-factor-evaluation/run.sh
./qlib-demos/09-strategy-and-backtest/run.sh
```

Expected:

- `01` reports all five instruments and a valid calendar.
- `02` prints OHLCV rows from multiple instruments.
- `03` prints populated expression rows from multiple instruments.
- `06` returns finite multi-instrument IC/RankIC metrics rather than single-instrument `NaN` metrics.
- `09` produces non-empty top-k return and turnover output.

- [ ] **Step 4: Inspect final repository state**

Run:

```bash
git status --short
git log -6 --oneline
git diff HEAD~4..HEAD --stat
```

Expected: only intentionally uncommitted plan tracking changes, if any; recent commits cleanly separate the prior repair, provider code, launcher/docs, and generated data.

- [ ] **Step 5: Stop on any verification defect**

If a command fails, do not patch during this verification task. Start a separate red-green bugfix task for the exact failure, rerun all commands in this task, and commit the exact tested correction before reporting completion. If all commands pass, do not create an empty commit.
