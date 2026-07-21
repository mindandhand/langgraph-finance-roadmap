import argparse
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "qlib-demos"))

import download_to_qlib


class SharedInstrumentEnvironmentTest(unittest.TestCase):
    env_script = ROOT / "qlib-demos/qlib_env.sh"

    def test_shared_environment_exports_default_instruments(self) -> None:
        result = subprocess.run(
            [
                "bash",
                "-c",
                'source "$1" && printf "%s" "$QLIB_INSTRUMENTS"',
                "bash",
                str(self.env_script),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            "sh510050,sh510300,sh510500,sz159915,sh588000",
            result.stdout,
        )

    def test_shared_environment_preserves_caller_override(self) -> None:
        result = subprocess.run(
            [
                "bash",
                "-c",
                'QLIB_INSTRUMENTS="custom"; source "$1" && '
                'printf "%s" "$QLIB_INSTRUMENTS"',
                "bash",
                str(self.env_script),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual("custom", result.stdout)

    def test_all_run_scripts_source_shared_environment(self) -> None:
        run_scripts = sorted((ROOT / "qlib-demos").glob("*/run.sh"))

        self.assertEqual(14, len(run_scripts))
        for run_script in run_scripts:
            with self.subTest(run_script=run_script):
                contents = run_script.read_text()
                self.assertIn(
                    'source "$SCRIPT_DIR/../qlib_env.sh"', contents
                )
                self.assertNotIn(
                    'export QLIB_INSTRUMENTS="sh510300"', contents
                )


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


class SafeProviderPublicationTest(unittest.TestCase):
    @staticmethod
    def make_frame(dates: list[str], offset: float = 0.0) -> pd.DataFrame:
        row_count = len(dates)
        values = np.arange(row_count, dtype=np.float32) + offset
        return pd.DataFrame(
            {
                "open": values + 1,
                "close": values + 2,
                "high": values + 3,
                "low": values + 0.5,
                "volume": values + 100,
                "amount": values + 1000,
                "factor": np.ones(row_count, dtype=np.float32),
            },
            index=pd.to_datetime(dates),
        )

    def setUp(self) -> None:
        self.spec = download_to_qlib.InstrumentSpec(
            "510050", "sh510050", "上证50 ETF"
        )

    def test_validate_frame_accepts_complete_frame(self) -> None:
        download_to_qlib.validate_frame(
            self.make_frame(["2024-01-01", "2024-01-02"]), self.spec
        )

    def test_validate_frame_rejects_empty_frame_and_names_symbol(self) -> None:
        frame = self.make_frame([])

        with self.assertRaisesRegex(ValueError, "sh510050.*empty"):
            download_to_qlib.validate_frame(frame, self.spec)

    def test_validate_frame_rejects_missing_fields_and_names_them(self) -> None:
        frame = self.make_frame(["2024-01-01"]).drop(
            columns=["amount", "factor"]
        )

        with self.assertRaisesRegex(
            ValueError, "sh510050.*amount.*factor"
        ):
            download_to_qlib.validate_frame(frame, self.spec)

    def test_validate_frame_rejects_non_datetime_index(self) -> None:
        frame = self.make_frame(["2024-01-01"])
        frame.index = ["2024-01-01"]

        with self.assertRaisesRegex(ValueError, "sh510050.*DatetimeIndex"):
            download_to_qlib.validate_frame(frame, self.spec)

    def test_validate_frame_rejects_duplicate_dates(self) -> None:
        frame = self.make_frame(["2024-01-01", "2024-01-01"])

        with self.assertRaisesRegex(ValueError, "sh510050.*duplicate"):
            download_to_qlib.validate_frame(frame, self.spec)

    def test_validate_frame_rejects_non_monotonic_dates(self) -> None:
        frame = self.make_frame(["2024-01-02", "2024-01-01"])

        with self.assertRaisesRegex(ValueError, "sh510050.*monotonic"):
            download_to_qlib.validate_frame(frame, self.spec)

    def test_write_and_validate_complete_multi_instrument_provider(self) -> None:
        frames = {
            "sh510050": self.make_frame(
                ["2024-01-01", "2024-01-02"], 10
            ),
            "sh588000": self.make_frame(
                ["2024-01-02", "2024-01-03"], 20
            ),
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            download_to_qlib.validate_provider(out_dir, frames)

            calendar = (
                out_dir / "calendars/day.txt"
            ).read_text().splitlines()
            metadata = (
                out_dir / "instruments/all.txt"
            ).read_text().splitlines()
            feature_values = np.fromfile(
                out_dir / "features/sh588000/open.day.bin", dtype="<f4"
            )

        self.assertEqual(
            ["2024-01-01", "2024-01-02", "2024-01-03"], calendar
        )
        self.assertEqual(
            {"sh510050", "sh588000"},
            {line.split("\t")[0] for line in metadata},
        )
        self.assertEqual(1.0, feature_values[0])

    def test_validate_provider_rejects_missing_feature_and_names_path(self) -> None:
        frames = {
            "sh510050": self.make_frame(["2024-01-01", "2024-01-02"])
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            missing = out_dir / "features/sh510050/amount.day.bin"
            missing.unlink()

            with self.assertRaisesRegex(
                FileNotFoundError, "amount[.]day[.]bin"
            ):
                download_to_qlib.validate_provider(out_dir, frames)

    def test_validate_provider_names_misaligned_feature_path(self) -> None:
        frames = {
            "sh510050": self.make_frame(["2024-01-01", "2024-01-02"])
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            corrupt = out_dir / "features/sh510050/open.day.bin"
            with corrupt.open("ab") as feature_file:
                feature_file.write(b"x")

            with self.assertRaisesRegex(
                ValueError, "open[.]day[.]bin.*float32"
            ):
                download_to_qlib.validate_provider(out_dir, frames)

    def test_validate_provider_rejects_whole_float_truncation(self) -> None:
        frames = {
            "sh510050": self.make_frame(["2024-01-01", "2024-01-02"])
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            corrupt = out_dir / "features/sh510050/open.day.bin"
            corrupt.write_bytes(corrupt.read_bytes()[:-4])

            with self.assertRaisesRegex(
                ValueError, "open[.]day[.]bin.*length"
            ):
                download_to_qlib.validate_provider(out_dir, frames)

    def test_validate_provider_rejects_wrong_metadata_dates(self) -> None:
        frames = {
            "sh510050": self.make_frame(["2024-01-01", "2024-01-02"])
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            metadata = out_dir / "instruments/all.txt"
            metadata.write_text("sh510050\t2020-01-01\t2020-01-02\n")

            with self.assertRaisesRegex(
                ValueError, "all[.]txt.*metadata"
            ):
                download_to_qlib.validate_provider(out_dir, frames)

    def test_validate_provider_rejects_wrong_calendar_content(self) -> None:
        frames = {
            "sh510050": self.make_frame(["2024-01-01", "2024-01-02"])
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            calendar = out_dir / "calendars/day.txt"
            calendar.write_text("2024-01-01\n2024-01-09\n")

            with self.assertRaisesRegex(
                ValueError, "day[.]txt.*calendar"
            ):
                download_to_qlib.validate_provider(out_dir, frames)

    def test_validate_provider_rejects_wrong_feature_payload(self) -> None:
        frames = {
            "sh510050": self.make_frame(["2024-01-01", "2024-01-02"])
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            corrupt = out_dir / "features/sh510050/open.day.bin"
            values = np.fromfile(corrupt, dtype="<f4")
            values[-1] = 999.0
            values.tofile(corrupt)

            with self.assertRaisesRegex(
                ValueError, "open[.]day[.]bin.*payload"
            ):
                download_to_qlib.validate_provider(out_dir, frames)

    def test_validate_provider_rejects_unexpected_feature_artifacts(self) -> None:
        frames = {
            "sh510050": self.make_frame(["2024-01-01", "2024-01-02"])
        }

        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory) / "provider"
            download_to_qlib.write_provider(frames, out_dir)
            unexpected_dir = out_dir / "features/sh999999"
            unexpected_dir.mkdir()

            with self.assertRaisesRegex(
                ValueError, "features.*unexpected"
            ):
                download_to_qlib.validate_provider(out_dir, frames)

    def test_publish_provider_restores_original_target_on_swap_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            target = parent / "qlib-data"
            staging = parent / "staging"
            target.mkdir()
            staging.mkdir()
            (target / "marker.txt").write_text("original")
            (staging / "marker.txt").write_text("replacement")

            def replace_except_staging(source: Path, destination: Path) -> None:
                if source == staging:
                    raise OSError("simulated staging swap failure")
                source.replace(destination)

            with mock.patch.object(
                download_to_qlib,
                "_replace_path",
                side_effect=replace_except_staging,
            ):
                with self.assertRaisesRegex(OSError, "staging swap failure"):
                    download_to_qlib.publish_provider(staging, target)

            self.assertEqual("original", (target / "marker.txt").read_text())
            self.assertFalse((parent / ".qlib-data.backup").exists())

    def test_publish_provider_recovers_backup_only_state_before_failed_swap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            target = parent / "qlib-data"
            backup = parent / ".qlib-data.backup"
            staging = parent / "staging"
            backup.mkdir()
            staging.mkdir()
            (backup / "marker.txt").write_text("recoverable-original")
            (staging / "marker.txt").write_text("replacement")

            def replace_except_staging(source: Path, destination: Path) -> None:
                if source == staging:
                    raise OSError("simulated staging swap failure")
                source.replace(destination)

            with mock.patch.object(
                download_to_qlib,
                "_replace_path",
                side_effect=replace_except_staging,
            ):
                with self.assertRaisesRegex(OSError, "staging swap failure"):
                    download_to_qlib.publish_provider(staging, target)

            self.assertEqual(
                "recoverable-original", (target / "marker.txt").read_text()
            )
            self.assertFalse(backup.exists())

    def test_publish_provider_prefers_target_over_stale_backup_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            target = parent / "qlib-data"
            backup = parent / ".qlib-data.backup"
            staging = parent / "staging"
            target.mkdir()
            backup.mkdir()
            staging.mkdir()
            (target / "marker.txt").write_text("authoritative-target")
            (backup / "marker.txt").write_text("stale-backup")

            def replace_except_staging(source: Path, destination: Path) -> None:
                if source == staging:
                    raise OSError("simulated staging swap failure")
                source.replace(destination)

            with mock.patch.object(
                download_to_qlib,
                "_replace_path",
                side_effect=replace_except_staging,
            ):
                with self.assertRaisesRegex(OSError, "staging swap failure"):
                    download_to_qlib.publish_provider(staging, target)

            self.assertEqual(
                "authoritative-target", (target / "marker.txt").read_text()
            )
            self.assertFalse(backup.exists())

    def test_selected_instruments_uses_defaults_without_override(self) -> None:
        args = argparse.Namespace(symbol=None, qlib_symbol=None)

        self.assertEqual(
            download_to_qlib.DEFAULT_INSTRUMENTS,
            download_to_qlib.selected_instruments(args),
        )

    def test_selected_instruments_builds_paired_override(self) -> None:
        args = argparse.Namespace(symbol="123456", qlib_symbol="sz123456")

        self.assertEqual(
            (
                download_to_qlib.InstrumentSpec(
                    "123456", "sz123456", "Custom ETF"
                ),
            ),
            download_to_qlib.selected_instruments(args),
        )

    def test_selected_instruments_rejects_incomplete_override_pair(self) -> None:
        for args in (
            argparse.Namespace(symbol="510300", qlib_symbol=None),
            argparse.Namespace(symbol=None, qlib_symbol="sh510300"),
        ):
            with self.subTest(args=args):
                with self.assertRaisesRegex(
                    ValueError, "--symbol.*--qlib-symbol"
                ):
                    download_to_qlib.selected_instruments(args)

    def test_download_all_collects_every_validated_frame(self) -> None:
        specs = download_to_qlib.DEFAULT_INSTRUMENTS[:2]
        downloaded = [
            self.make_frame(["2024-01-01"], 10),
            self.make_frame(["2024-01-02"], 20),
        ]

        with mock.patch.object(
            download_to_qlib, "download", side_effect=downloaded
        ) as download_mock:
            frames = download_to_qlib.download_all(
                specs, "20240101", "20240131", "qfq"
            )

        self.assertEqual([spec.qlib_symbol for spec in specs], list(frames))
        self.assertEqual(
            [
                mock.call("510050", "20240101", "20240131", "qfq"),
                mock.call("510300", "20240101", "20240131", "qfq"),
            ],
            download_mock.call_args_list,
        )

    def test_download_all_names_failed_instrument_and_preserves_cause(self) -> None:
        specs = download_to_qlib.DEFAULT_INSTRUMENTS[:2]
        cause = ValueError("network returned no rows")

        with mock.patch.object(
            download_to_qlib,
            "download",
            side_effect=[self.make_frame(["2024-01-01"]), cause],
        ):
            with self.assertRaisesRegex(
                RuntimeError, "sh510300.*510300"
            ) as raised:
                download_to_qlib.download_all(
                    specs, "20240101", "20240131", "qfq"
                )

        self.assertIs(cause, raised.exception.__cause__)

    def test_selected_instruments_rejects_path_traversal_symbol(self) -> None:
        args = argparse.Namespace(symbol="510050", qlib_symbol="../../victim")

        with self.assertRaisesRegex(ValueError, "qlib_symbol"):
            download_to_qlib.selected_instruments(args)

    def test_selected_instruments_rejects_empty_symbol(self) -> None:
        args = argparse.Namespace(symbol="510050", qlib_symbol="   ")

        with self.assertRaisesRegex(ValueError, "qlib_symbol"):
            download_to_qlib.selected_instruments(args)

    def test_selected_instruments_rejects_invalid_source_symbol(self) -> None:
        args = argparse.Namespace(symbol="not-an-etf", qlib_symbol="sh510050")

        with self.assertRaisesRegex(ValueError, "source_symbol"):
            download_to_qlib.selected_instruments(args)

    def test_download_all_rejects_duplicate_qlib_symbols_before_download(self) -> None:
        specs = (
            download_to_qlib.InstrumentSpec("510050", "sh510050", "first"),
            download_to_qlib.InstrumentSpec("510300", "sh510050", "second"),
        )

        with mock.patch.object(download_to_qlib, "download") as download_mock:
            with self.assertRaisesRegex(ValueError, "duplicate.*sh510050"):
                download_to_qlib.download_all(
                    specs, "20240101", "20240131", "qfq"
                )

        download_mock.assert_not_called()

    def test_write_provider_rejects_path_traversal_without_external_write(self) -> None:
        frame = self.make_frame(["2024-01-01"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out_dir = root / "provider"
            escaped = root / "victim"

            with self.assertRaisesRegex(ValueError, "qlib_symbol"):
                download_to_qlib.write_provider({"../../victim": frame}, out_dir)

            self.assertFalse(escaped.exists())

    def test_main_download_failure_leaves_existing_provider_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "qlib-data"
            target.mkdir()
            marker = target / "marker.txt"
            marker.write_text("original")
            args = argparse.Namespace(
                symbol="510050",
                qlib_symbol="sh510050",
                start="20240101",
                end="20240131",
                adjust="qfq",
                out_dir=str(target),
            )

            with mock.patch.object(download_to_qlib, "parse_args", return_value=args):
                with mock.patch.object(
                    download_to_qlib,
                    "download",
                    side_effect=OSError("network unavailable"),
                ):
                    with self.assertRaisesRegex(RuntimeError, "sh510050"):
                        download_to_qlib.main()

            self.assertEqual("original", marker.read_text())

    def test_main_staging_validation_failure_does_not_publish(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "qlib-data"
            target.mkdir()
            marker = target / "marker.txt"
            marker.write_text("original")
            args = argparse.Namespace(
                symbol="510050",
                qlib_symbol="sh510050",
                start="20240101",
                end="20240131",
                adjust="qfq",
                out_dir=str(target),
            )

            with mock.patch.object(download_to_qlib, "parse_args", return_value=args):
                with mock.patch.object(
                    download_to_qlib,
                    "download",
                    return_value=self.make_frame(["2024-01-01"]),
                ):
                    with mock.patch.object(
                        download_to_qlib,
                        "validate_provider",
                        side_effect=ValueError("staged provider is corrupt"),
                    ):
                        with mock.patch.object(
                            download_to_qlib, "publish_provider"
                        ) as publish_mock:
                            with self.assertRaisesRegex(
                                ValueError, "staged provider is corrupt"
                            ):
                                download_to_qlib.main()

            publish_mock.assert_not_called()
            self.assertEqual("original", marker.read_text())

    def test_parse_args_rejects_incomplete_override_with_usage_error(self) -> None:
        with mock.patch.object(
            sys,
            "argv",
            ["download_to_qlib.py", "--symbol", "510050"],
        ):
            with mock.patch("sys.stderr"):
                with self.assertRaises(SystemExit) as raised:
                    download_to_qlib.parse_args()

        self.assertEqual(2, raised.exception.code)


if __name__ == "__main__":
    unittest.main()
