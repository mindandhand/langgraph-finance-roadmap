import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "qlib-demos"))

from download_to_qlib import write_features


class QlibExpressionsRunTest(unittest.TestCase):
    def test_run_script_prints_rows_from_bundled_provider(self) -> None:
        result = subprocess.run(
            ["bash", str(ROOT / "qlib-demos/03-qlib-expressions/run.sh")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("rolling_mom20_rank", result.stdout)
        self.assertNotIn("Empty DataFrame", result.stdout)

    def test_feature_binary_starts_with_calendar_index(self) -> None:
        calendar = pd.date_range("2024-01-01", periods=3, freq="D")
        frame = pd.DataFrame(
            {"close": np.array([10.0, 11.0], dtype=np.float32)},
            index=calendar[1:],
        )

        with tempfile.TemporaryDirectory() as directory:
            write_features(frame, "test", calendar, Path(directory))
            values = np.fromfile(
                Path(directory) / "features/test/close.day.bin", dtype="<f4"
            )

        np.testing.assert_array_equal(
            np.array([1.0, 10.0, 11.0], dtype=np.float32), values
        )


if __name__ == "__main__":
    unittest.main()
