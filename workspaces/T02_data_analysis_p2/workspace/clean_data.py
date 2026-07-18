"""
Data Cleaning Pipeline — Pandas
================================
Cleans a CSV dataset with five operations in order:
  1. Remove duplicate rows
  2. Fill missing numeric values with column median
  3. Drop rows where >50% of columns are null
  4. Convert date strings to datetime
  5. Strip whitespace from string columns
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path


def clean_dataframe(df: pd.DataFrame) -> tuple:
    """
    Apply the full cleaning pipeline to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw input DataFrame.

    Returns
    -------
    tuple[pd.DataFrame, int, int]
        (cleaned_df, row_count_before, row_count_after)
    """
    before = len(df)
    result = df.copy()

    # --- 1. Remove duplicate rows -------------------------------------------
    result = result.drop_duplicates()

    # --- 2. Fill missing numeric values with column median ------------------
    numeric_cols = result.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        median_val = result[col].median()
        result[col] = result[col].fillna(median_val)

    # --- 3. Drop rows where >50% of columns are null ------------------------
    # Keep a row if at least ceil(50% + 1) columns are non-null
    threshold = result.shape[1] // 2 + 1
    result = result.dropna(thresh=threshold)

    # --- 4. Convert date strings to datetime --------------------------------
    for col in result.select_dtypes(include=['object']).columns:
        sample = result[col].dropna().head(20)
        if len(sample) == 0:
            continue
        try:
            parsed = pd.to_datetime(sample, errors='coerce')
            # If at least 50% of sampled values parsed as valid dates → convert whole column
            if parsed.notna().sum() / len(sample) >= 0.5:
                result[col] = pd.to_datetime(result[col], errors='coerce')
        except (ValueError, TypeError):
            pass

    # --- 5. Strip whitespace from string columns ----------------------------
    for col in result.select_dtypes(include=['object']).columns:
        result[col] = result[col].str.strip()

    after = len(result)
    return result, before, after


def clean_csv(input_path: str, output_path: str | None = None) -> tuple:
    """
    Load a CSV, clean it, and optionally save the result.

    Parameters
    ----------
    input_path : str
        Path to the input CSV file.
    output_path : str | None
        If provided, write the cleaned DataFrame to this path.

    Returns
    -------
    tuple[pd.DataFrame, int, int]
        (cleaned_df, row_count_before, row_count_after)
    """
    df = pd.read_csv(input_path)
    cleaned, before, after = clean_dataframe(df)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(output_path, index=False)

    return cleaned, before, after


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_data.py <input_csv> [output_csv]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    cleaned, before, after = clean_csv(input_file, output_file)
    print(f"Rows before cleaning: {before}")
    print(f"Rows after cleaning:  {after}")
    print(f"Rows removed:         {before - after}")

    if output_file:
        print(f"Cleaned data written to: {output_file}")
