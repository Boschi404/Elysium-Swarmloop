"""Tests for the data cleaning pipeline."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from cleaning_pipeline import clean_dataframe


def make_test_df():
    """Build a small DataFrame with known issues."""
    return pd.DataFrame({
        "id":        [1, 2, 3, 1, 2, np.nan],
        "name":      ["Alice", " Bob ", "Charlie", "Alice", " Bob ", ""],
        "age":       [30, 28, np.nan, 30, 28, np.nan],
        "salary":    [70000, 55000, 80000, 70000, 55000, np.nan],
        "score":     [85.0, 92.0, np.nan, 85.0, 92.0, np.nan],
    })


def test_deduplication():
    df = make_test_df()
    before = len(df)
    cleaned = clean_dataframe(df)
    after = len(cleaned)
    # Must remove at least 2 exact duplicates (rows 0/3 and 1/4)
    assert after <= before - 2, f"Expected <= {before - 2} rows, got {after}"
    # Verify no two rows are identical across all columns
    assert not cleaned.duplicated().any(), "Row-level duplicates remain"


def test_median_fill():
    df = make_test_df()
    cleaned = clean_dataframe(df)
    # age has NaN in row 3 (index 2); should be median of [30, 28, NaN, 30, 28, NaN]
    # median of [30, 28, 30, 28] = 29.0
    assert cleaned.loc[2, "age"] == 29.0, f"Expected 29.0, got {cleaned.loc[2, 'age']}"
    assert not cleaned["salary"].isna().any(), "Salary NaNs not filled"


def test_drop_excessive_nulls():
    df = make_test_df()
    # Add a row with >50% nulls (3+ nulls out of 5 columns)
    df.loc[len(df)] = [np.nan, np.nan, np.nan, 50000, np.nan]  # 4/5 = 80% null
    count_before = len(df)
    cleaned = clean_dataframe(df)
    assert len(cleaned) < count_before, "All-null row not dropped"


def test_date_conversion():
    df = pd.DataFrame({
        "id":   [1, 2],
        "date": ["2023-01-15", "2022-06-10"],
        "val":  [10, 20],
    })
    cleaned = clean_dataframe(df)
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"]), "date not converted to datetime"


def test_whitespace_stripping():
    df = make_test_df()
    cleaned = clean_dataframe(df)
    for val in cleaned["name"]:
        assert val == val.strip(), f"Whitespace not stripped from '{val}'"


def test_end_to_end():
    df = make_test_df()
    before = len(df)
    cleaned = clean_dataframe(df)
    after = len(cleaned)
    assert after < before, "End-to-end: row count must decrease"
    assert after == before - 2, f"Expected {before - 2} rows, got {after}"
    for val in cleaned["name"]:
        assert val == val.strip(), f"Whitespace remains: '{val}'"


if __name__ == "__main__":
    test_deduplication()
    test_median_fill()
    test_drop_excessive_nulls()
    test_date_conversion()
    test_whitespace_stripping()
    test_end_to_end()
    print("All tests passed.")
