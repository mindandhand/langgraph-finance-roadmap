import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "qlib-demos"))

import download_to_qlib


class MultiEtfProviderModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.frames = {
            "sh588000": pd.DataFrame(
                {"close": np.array([20.0, 21.0], dtype=np.float32)},
                index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
            ),
            "sh510050": pd.DataFrame(
                {"close": np.array([10.0, 11.0], dtype=np.float32)},
                index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
            ),
        }

    def test_default_instruments_have_expected_values_in_order(self) -> None:
        self.assertEqual(
            [
                ("510050", "sh510050", "上证50 ETF"),
                ("510300", "sh510300", "沪深300 ETF"),
                ("510500", "sh510500", "中证500 ETF"),
                ("159915", "sz159915", "创业板 ETF"),
                ("588000", "sh588000", "科创50 ETF"),
            ],
            [
                (spec.source_symbol, spec.qlib_symbol, spec.name)
                for spec in download_to_qlib.DEFAULT_INSTRUMENTS
            ],
        )

    def test_build_calendar_returns_sorted_union(self) -> None:
        calendar = download_to_qlib.build_calendar(self.frames)

        pd.testing.assert_index_equal(
            pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            calendar,
        )

    def test_build_calendar_rejects_empty_mapping(self) -> None:
        with self.assertRaises(ValueError):
            download_to_qlib.build_calendar({})

    def test_build_calendar_sorts_and_removes_duplicates_within_frame(self) -> None:
        frame = pd.DataFrame(
            {"close": np.array([12.0, 10.0, 11.0], dtype=np.float32)},
            index=pd.to_datetime(
                ["2024-01-02", "2024-01-01", "2024-01-02"]
            ),
        )

        calendar = download_to_qlib.build_calendar({"sh510050": frame})

        pd.testing.assert_index_equal(
            pd.to_datetime(["2024-01-01", "2024-01-02"]), calendar
        )

    def test_build_calendar_normalizes_date_like_string_index(self) -> None:
        frame = pd.DataFrame(
            {"close": np.array([11.0, 10.0], dtype=np.float32)},
            index=["2024-01-02", "2024-01-01"],
        )

        calendar = download_to_qlib.build_calendar({"sh510050": frame})

        self.assertIsInstance(calendar, pd.DatetimeIndex)
        pd.testing.assert_index_equal(
            pd.to_datetime(["2024-01-01", "2024-01-02"]), calendar
        )

    def test_write_instruments_sorts_symbols_and_uses_frame_dates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            download_to_qlib.write_instruments(self.frames, Path(directory))
            contents = (
                Path(directory) / "instruments" / "all.txt"
            ).read_text()

        self.assertEqual(
            "sh510050\t2024-01-01\t2024-01-02\n"
            "sh588000\t2024-01-02\t2024-01-03\n",
            contents,
        )

    def test_write_features_keeps_union_calendar_start_index_header(self) -> None:
        calendar = pd.to_datetime(
            ["2024-01-01", "2024-01-02", "2024-01-03"]
        )

        with tempfile.TemporaryDirectory() as directory:
            download_to_qlib.write_features(
                self.frames["sh588000"],
                "sh588000",
                calendar,
                Path(directory),
            )
            values = np.fromfile(
                Path(directory) / "features/sh588000/close.day.bin",
                dtype="<f4",
            )

        np.testing.assert_array_equal(
            np.array([1.0, 20.0, 21.0], dtype=np.float32), values
        )


if __name__ == "__main__":
    unittest.main()
