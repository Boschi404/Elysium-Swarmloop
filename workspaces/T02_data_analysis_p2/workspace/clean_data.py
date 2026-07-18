#!/usr/bin/env python3
"""
Pandas Data Cleaning Pipeline

Cleans a CSV dataset by applying:
  1) Remove duplicate rows
  2) Fill missing numeric values with column median
  3) Drop rows where >50% of columns are null
  4) Convert date strings to datetime
  5) Strip whitespace from string columns

Usage:
    python clean_data.py [input_csv] [output_csv]

If no arguments are given, reads from stdin and writes to stdout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple

import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the five cleaning steps to a DataFrame and return the cleaned version.

    Args:
        df: Raw DataFrame loaded from CSV.

    Returns:
        Cleaned DataFrame with all transformations applied.
    """
    # Work on a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # ── 1) Remove duplicate rows ──────────────────────────────────────────
    df = df.drop_duplicates()

    # ── 2) Drop rows where >50% of columns are null ────────────────────────
    #   (Before fillna — otherwise fillna would rescue mostly-null rows)
    min_non_null = len(df.columns) / 2
    df = df.dropna(thresh=min_non_null)

    # ── 3) Fill missing numeric values with column median ─────────────────
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        median_val = df[col].median()
        if pd.notna(median_val):
            df.loc[:, col] = df[col].fillna(median_val)

    # ── 4) Convert date strings to datetime ────────────────────────────────
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                # errors='coerce' produces datetime64[ns] with NaT for unparsable
                converted = pd.to_datetime(df[col], errors="coerce")
                # Only accept conversion if at least one value was parseable
                if converted.notna().any():
                    df.loc[:, col] = converted
            except (ValueError, TypeError):
                pass  # column is not a date, leave as-is

    # ── 5) Strip whitespace from string columns ────────────────────────────
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        if df[col].dtype == "object":
            try:
                df.loc[:, col] = df[col].str.strip()
            except AttributeError:
                pass  # column contains non-string data (e.g. mixed Timestamps)

    return df


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV from *path*, auto-detecting common date columns."""
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: str | Path) -> None:
    """Write *df* to *path* as a CSV."""
    df.to_csv(path, index=False)


def run_pipeline(input_path: str | Path) -> Tuple[int, int, pd.DataFrame]:
    """Execute the full cleaning pipeline.

    Args:
        input_path: Path to the input CSV file.

    Returns:
        Tuple of (original_row_count, cleaned_row_count, cleaned_dataframe).
    """
    df_raw = load_csv(input_path)
    original_count = len(df_raw)
    df_clean = clean_dataframe(df_raw)
    cleaned_count = len(df_clean)
    return original_count, cleaned_count, df_clean


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean a CSV dataset with a standard data-cleaning pipeline."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Path to input CSV file (reads from stdin if omitted)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Path to write cleaned CSV (writes to stdout if omitted)",
    )
    args = parser.parse_args()

    # ── Load ────────────────────────────────────────────────────────────────
    if args.input:
        df = load_csv(args.input)
    else:
        df = pd.read_csv(sys.stdin)

    original_count = len(df)

    # ── Clean ───────────────────────────────────────────────────────────────
    df = clean_dataframe(df)
    cleaned_count = len(df)

    # ── Save / Report ───────────────────────────────────────────────────────
    if args.output:
        save_csv(df, args.output)
    else:
        df.to_csv(sys.stdout, index=False)

    print(f"\n# Cleaning complete: {original_count} rows → {cleaned_count} rows", file=sys.stderr)
    print(f"# Removed: {original_count - cleaned_count} rows", file=sys.stderr)


if __name__ == "__main__":
    main()
