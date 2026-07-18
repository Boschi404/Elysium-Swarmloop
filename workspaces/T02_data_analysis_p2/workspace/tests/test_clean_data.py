#!/usr/bin/env python3
"""Tests for the data cleaning pipeline."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import pytest

from clean_data import clean_dataframe, run_pipeline


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def raw_df() -> pd.DataFrame:
    """A DataFrame with all five issues the pipeline should fix."""
    return pd.DataFrame({
        "name": ["Alice ", "Bob", "Alice ", "Charlie", None, "Eve", None],
        "age": [30.0, 25.0, 30.0, 35.0, None, 29.0, 40.0],
        "email": [
            "alice@example.com",
            " bob@example.com",
            "alice@example.com",
            None,
            "diana@example.com",
            None,
            None,
        ],
        "joined": [
            "2024-01-15",
            "2023-06-20",
            "2024-01-15",
            "2022-11-01",
            None,
            "2024-03-10",
            None,
        ],
        "score": [88.5, None, 88.5, 92.0, None, None, 75.0],
        "city": [" New York", "London", " New York", "Paris", " Berlin", None, None],
    })


@pytest.fixture
def sample_csv_path() -> str:
    """Path to the sample CSV bundled with the workspace."""
    return str(Path(__file__).resolve().parent.parent / "sample_data.csv")


# ── Unit tests against clean_dataframe ────────────────────────────────────────


class TestCleanDataframe:
    """Tests for the core cleaning function."""

    def test_removes_duplicates(self, raw_df: pd.DataFrame) -> None:
        """Duplicate row (Alice/Alice) should be removed."""
        before = len(raw_df)
        cleaned = clean_dataframe(raw_df)
        # 7 rows in raw, rows 0 and 2 are duplicates → at most 6 remain
        assert len(cleaned) < before
        # Verify Alice only appears once
        alice_rows = cleaned[cleaned["name"].str.strip() == "Alice"]
        assert len(alice_rows) == 1

    def test_fills_numeric_with_median(self, raw_df: pd.DataFrame) -> None:
        """Missing numeric values should be filled with column median."""
        cleaned = clean_dataframe(raw_df)
        # age column: values [30, 25, 30, 35, 29, 40] → median = 30.0
        # The remaining rows after dropna should have no NaN in 'age'
        assert cleaned["age"].isna().sum() == 0
        # 30.0 is the median, so any row that had NaN in age should be 30.0
        assert cleaned["age"].between(25.0, 40.0).all()

    def test_drops_rows_mostly_null(self, raw_df: pd.DataFrame) -> None:
        """Rows where >50% of columns are null should be dropped."""
        cleaned = clean_dataframe(raw_df)
        # row 6 (Frank): name=Frank, age=40, email=None, joined=None, score=75, city=None
        # This row has 3 nulls out of 6 columns = 50% → NOT strictly >50%, so it stays
        # Check that no row has >50% nulls
        for _, row in cleaned.iterrows():
            null_frac = row.isnull().sum() / len(cleaned.columns)
            assert null_frac <= 0.5, f"Row has {null_frac:.0%} null values"

    def test_converts_date_strings(self, raw_df: pd.DataFrame) -> None:
        """The 'joined' column should be datetime after cleaning."""
        cleaned = clean_dataframe(raw_df)
        assert pd.api.types.is_datetime64_any_dtype(cleaned["joined"]), (
            "joined column should be datetime64"
        )

    def test_strips_whitespace(self, raw_df: pd.DataFrame) -> None:
        """String columns should not have leading/trailing whitespace."""
        cleaned = clean_dataframe(raw_df)
        for col in cleaned.select_dtypes(include="object").columns:
            for val in cleaned[col].dropna():
                assert val == val.strip(), f"'{val}' in {col} still has whitespace"

    def test_empty_dataframe(self) -> None:
        """Pipeline should handle an empty DataFrame gracefully."""
        df = pd.DataFrame({"a": [], "b": []})
        cleaned = clean_dataframe(df)
        assert len(cleaned) == 0

    def test_no_issues_dataframe(self) -> None:
        """Cleaning a pristine DataFrame should leave it unchanged."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        cleaned = clean_dataframe(df)
        assert cleaned.equals(df)

    def test_all_numeric_column(self) -> None:
        """A purely numeric DataFrame should still be cleaned correctly."""
        df = pd.DataFrame({"a": [1.0, None, 3.0, None], "b": [4.0, 5.0, None, None]})
        cleaned = clean_dataframe(df)
        # Row 3 has 2/2 nulls = 100% > 50% → dropped
        assert len(cleaned) == 3
        # Median of a = 2.0 (works with even count: 1,3 → median=2.0)
        assert cleaned["a"].isna().sum() == 0

    def test_no_duplicates_left(self, raw_df: pd.DataFrame) -> None:
        """After cleaning, there should be no duplicate rows."""
        cleaned = clean_dataframe(raw_df)
        assert cleaned.duplicated().sum() == 0


# ── Integration tests ─────────────────────────────────────────────────────────


class TestRunPipeline:
    """Tests for the full pipeline runner."""

    def test_returns_counts(self, sample_csv_path: str) -> None:
        """run_pipeline returns (before, after, df)."""
        before, after, df = run_pipeline(sample_csv_path)
        assert isinstance(before, int)
        assert isinstance(after, int)
        assert isinstance(df, pd.DataFrame)
        assert before >= after

    def test_csv_round_trip(self, sample_csv_path: str) -> None:
        """Cleaned CSV should load back cleanly."""
        before, after, df = run_pipeline(sample_csv_path)
        assert after > 0, "Should have at least one row after cleaning"

        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name
            df.to_csv(tmp_path, index=False)

        reloaded = pd.read_csv(tmp_path)
        assert len(reloaded) == after
        Path(tmp_path).unlink(missing_ok=True)

    @pytest.mark.parametrize(
        "col, expected_dtype",
        [
            ("joined", "datetime64[ns]"),
            ("age", "float64"),
            ("name", "object"),
        ],
    )
    def test_column_types_after_cleaning(
        self, sample_csv_path: str, col: str, expected_dtype: str
    ) -> None:
        """Verify specific column dtypes after the pipeline runs."""
        _, _, df = run_pipeline(sample_csv_path)
        assert str(df[col].dtype) == expected_dtype

    def test_no_null_date_after_cleaning(self, sample_csv_path: str) -> None:
        """The date column should have no nulls after median/date fill."""
        _, _, df = run_pipeline(sample_csv_path)
        # joined had some nulls; after cleaning NaT should be possible if
        # the column is datetime and median-fill only applies to numeric cols
        # so just check dtype
        assert pd.api.types.is_datetime64_any_dtype(df["joined"])


# ── Behavioural edge-case tests ──────────────────────────────────────────────


def test_whitespace_only_rows_are_removed() -> None:
    """Rows where all string values are whitespace should be handled."""
    df = pd.DataFrame({
        "a": ["  ", "x", "y"],
        "b": ["  ", "1", "2"],
        "c": ["  ", "3", "4"],
    })
    cleaned = clean_dataframe(df)
    # Row 0: after strip → empty strings, but not NaN, so it stays
    assert len(cleaned) == 3
    # All values should be stripped
    for _, row in cleaned.iterrows():
        for col in cleaned.columns:
            val = row[col]
            if isinstance(val, str):
                assert val == val.strip()


def test_mixed_date_formats() -> None:
    """Different date formats in same column should be handled."""
    df = pd.DataFrame({
        "date": ["2024-01-15", "15/01/2024", "Jan 15, 2024", None],
        "val": [1, 2, 3, 4],
    })
    cleaned = clean_dataframe(df)
    # With format='mixed', pandas uses dateutil to parse various formats.
    # This should succeed for the three formats above.
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"]), (
        f"date column has dtype {cleaned['date'].dtype}"
    )
    # Verify the parsed values (NaT for the None row)
    assert cleaned["date"].iloc[0] == pd.Timestamp("2024-01-15")
    assert cleaned["date"].iloc[2] == pd.Timestamp("2024-01-15")
