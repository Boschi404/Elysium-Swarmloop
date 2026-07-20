"""
T02_data_analysis — Data Cleaning Pipeline
============================================
Reads a CSV, applies cleaning transformations, and reports row counts
before and after.

Transformations:
    1. Remove duplicate rows
    2. Fill missing numeric values with column median
    3. Drop rows where >50% of columns are null
    4. Convert date-like string columns to datetime
    5. Strip whitespace from string/object columns
"""

import pandas as pd
import sys
from pathlib import Path


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the five cleaning steps to *df* and return the cleaned copy."""

    df = df.copy()

    # 1. Remove duplicate rows
    before_dedup = len(df)
    df = df.drop_duplicates()
    after_dedup = len(df)
    if after_dedup < before_dedup:
        print(f"  Removed {before_dedup - after_dedup} duplicate row(s).")

    # 2. Fill missing numeric values with column median
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        if df[col].isna().all():
            continue
        null_count = df[col].isna().sum()
        if null_count > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  Filled {int(null_count)} null(s) in '{col}' with median {median_val:.4f}.")

    # 3. Drop rows where >50% of columns are null
    thresh = len(df.columns) / 2
    before_drop = len(df)
    df = df.dropna(thresh=thresh)
    after_drop = len(df)
    if after_drop < before_drop:
        print(f"  Dropped {before_drop - after_drop} row(s) with >50% nulls.")

    # 4. Convert date-like string columns to datetime
    obj_cols = df.select_dtypes(include="object").columns
    for col in obj_cols:
        # Heuristic: sample up to 20 non-null values; if most parse as dates, convert
        sample = df[col].dropna().head(20)
        if len(sample) == 0:
            continue
        parsed = pd.to_datetime(sample, errors="coerce")
        # If >= 50% of sampled values parse successfully, convert the whole column
        if parsed.notna().sum() / len(sample) >= 0.5:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            print(f"  Converted '{col}' to datetime.")

    # 5. Strip whitespace from all string/object columns
    for col in obj_cols:
        if df[col].dtype == "object":
            stripped = df[col].astype(str).str.strip()
            # Only keep the stripped result if it actually differs somewhere
            if not stripped.equals(df[col].astype(str)):
                df[col] = stripped
                print(f"  Stripped whitespace from '{col}'.")

    return df


def clean_csv(
    input_path: str,
    output_path: str | None = None,
) -> tuple[int, int]:
    """Read *input_path*, clean the data, optionally write the result."""

    df = pd.read_csv(input_path)
    rows_before = len(df)
    print(f"Rows before cleaning: {rows_before}")
    print(f"Columns: {list(df.columns)}")
    print()

    df_clean = clean_dataframe(df)

    rows_after = len(df_clean)
    print(f"\nRows after cleaning:  {rows_after}")
    print(f"Rows removed:         {rows_before - rows_after}")

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_csv(out, index=False)
        print(f"Cleaned data written to {out}")

    return rows_before, rows_after


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        print("Usage: python cleaning_pipeline.py <input_csv> [output_csv]")
        sys.exit(1)

    inp = args[0]
    out = args[1] if len(args) > 1 else None
    before, after = clean_csv(inp, out)
    print(f"\nSummary: {before} -> {after} rows ({before - after} removed)")
