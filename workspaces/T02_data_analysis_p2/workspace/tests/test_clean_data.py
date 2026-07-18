"""Tests for the data cleaning pipeline."""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ensure the workspace is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from clean_data import clean_dataframe, clean_csv

SAMPLE_CSV = Path(__file__).resolve().parent.parent / "sample_data.csv"


def test_remove_duplicates():
    df = pd.DataFrame({"a": [1, 2, 2, 3], "b": ["x", "y", "y", "z"]})
    cleaned, before, after = clean_dataframe(df)
    assert before == 4
    assert after == 3, f"Expected 3 rows after dedup, got {after}"
    assert not cleaned.duplicated().any()


def test_fill_numeric_median():
    df = pd.DataFrame({"x": [1, 2, np.nan, 10], "y": [5, np.nan, np.nan, 8]})
    cleaned, *_ = clean_dataframe(df)
    # median of x = (1+2+10)/3 sorted: [1,2,10] → median = 2
    assert cleaned["x"].iloc[2] == 2.0, f"Expected 2.0, got {cleaned['x'].iloc[2]}"
    # median of y = [5, 8] → median = 6.5
    assert cleaned["y"].iloc[1] == 6.5, f"Expected 6.5, got {cleaned['y'].iloc[1]}"
    assert cleaned["y"].iloc[2] == 6.5


def test_drop_high_null_rows():
    # Fill-numeric happens BEFORE row-drop (per spec order: step 2 then step 3).
    # Row 1 has numeric NaN in a, c, d → filled with median → becomes 3/4 non-null → kept.
    df = pd.DataFrame({
        "a": [1, np.nan, 3],
        "b": ["x", np.nan, "z"],
        "c": [10, np.nan, 30],
        "d": [100, np.nan, np.nan],
    })
    cleaned, before, after = clean_dataframe(df)
    assert before == 3
    # Row 0: 4/4 non-null → kept
    # Row 1: all NaN → numeric fill gives a=2.0, c=20.0, d=100.0 → 3/4 non-null → kept (>= threshold=3)
    # Row 2: a=3, b=z, c=30, d=NaN → 3/4 non-null → kept
    assert after == 3, f"Expected 3 rows (numeric fill fills row 1 before drop), got {after}"


def test_date_conversion():
    df = pd.DataFrame({"date": ["2023-01-15", "2022-06-01", "2021-03-20"]})
    cleaned, *_ = clean_dataframe(df)
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"]), "date column should be datetime64"


def test_strip_whitespace():
    df = pd.DataFrame({"name": ["  Alice  ", "  Bob", "Charlie "], "role": ["dev", "  qa  ", "ops"]})
    cleaned, *_ = clean_dataframe(df)
    assert cleaned["name"].iloc[0] == "Alice", f"Expected 'Alice', got '{cleaned['name'].iloc[0]}'"
    assert cleaned["role"].iloc[1] == "qa", f"Expected 'qa', got '{cleaned['role'].iloc[1]}'"


def test_full_pipeline_on_sample():
    """End-to-end test against sample_data.csv (written with known expected results)."""
    df = pd.read_csv(SAMPLE_CSV)
    cleaned, before, after = clean_dataframe(df)

    # sample_data.csv has 11 rows:
    # - Row 0: " Alice " (1 leading space)
    # - Row 1: Bob
    # - Row 2: "  Charlie " (2 leading spaces)
    # - Row 3: "  Alice " (2 leading spaces — different from row 0 → NOT a dedup)
    # - Row 4: David (missing Age, Salary)
    # - Row 5: all-null row (only Join_Date present)
    # - Row 6: Eve (bad date)
    # - Row 7: Frank
    # - Row 8: "  Alice " (same as row 3)
    # - Row 9: all-null row (same as row 5)
    # - Row 10: Grace (missing Age, Salary)
    #
    # Pipeline:
    #   Step 1 dedup: 11 → 9  (remove row 8 = row 3, row 9 = row 5)
    #   Step 2 fill numeric: Age median 30.0, Salary median 55000
    #   Step 3 drop >50% null: row 5 has only 3/6 non-null → dropped
    #   So expected: 8 rows
    assert before == 11, f"Expected 11 raw rows, got {before}"
    assert after == 8, f"Expected 8 rows after cleaning, got {after}"
    assert after > 0, "Should have at least 1 row after cleaning"

    # Verify salary NaN filled
    assert cleaned["Salary"].notna().all(), "No NaN should remain in Salary"
    # Verify dates parsed
    if "Join_Date" in cleaned.columns:
        assert pd.api.types.is_datetime64_any_dtype(cleaned["Join_Date"]), "Join_Date should be datetime"

    # Verify whitespace stripped
    for col in cleaned.select_dtypes(include=["object"]).columns:
        assert not cleaned[col].str.match(r"^\s|\s$").any(), f"Column '{col}' still has leading/trailing whitespace"

    print(f"\n[test_full_pipeline] {before} → {after} rows")
    print(f"[test_full_pipeline] Columns: {list(cleaned.columns)}")
    print(f"[test_full_pipeline] Dtypes:\n{cleaned.dtypes}")


if __name__ == "__main__":
    test_remove_duplicates()
    print("✓ test_remove_duplicates")
    test_fill_numeric_median()
    print("✓ test_fill_numeric_median")
    test_drop_high_null_rows()
    print("✓ test_drop_high_null_rows")
    test_date_conversion()
    print("✓ test_date_conversion")
    test_strip_whitespace()
    print("✓ test_strip_whitespace")
    test_full_pipeline_on_sample()
    print("✓ test_full_pipeline_on_sample")
    print("\n✅ All tests passed.")
