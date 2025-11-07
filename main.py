#!/usr/bin/env python3
"""
Revolut Extract Generator

Processes Revolut transaction CSV exports for easier reconciliation.
Filters specific columns and prepares data for accounting purposes.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd


# Columns to keep from the original Revolut CSV
COLUMNS_TO_KEEP = [
    "Date completed (UTC)",
    "Description",
    "Orig currency",
    "Orig amount",
    "Amount",
    "Balance",
    "Exchange rate",
]


def process_revolut_csv(input_file: Path, output_file: Path) -> None:
    """
    Process Revolut CSV export, filtering to specific columns.

    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Check if all required columns exist in the input file
        missing_columns = [col for col in COLUMNS_TO_KEEP if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing columns in input file: {', '.join(missing_columns)}", file=sys.stderr)
            print(f"\nAvailable columns: {', '.join(df.columns)}", file=sys.stderr)
            sys.exit(1)

        # Filter to only the columns we want
        df_filtered = df[COLUMNS_TO_KEEP]

        # Convert date column to datetime for proper sorting
        df_filtered["Date completed (UTC)"] = pd.to_datetime(df_filtered["Date completed (UTC)"])

        # Sort by date, oldest first
        df_filtered = df_filtered.sort_values("Date completed (UTC)", ascending=True)

        # Write to output file
        df_filtered.to_csv(output_file, index=False)

        print(f"Successfully processed {len(df_filtered)} transactions")
        print(f"Output written to: {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: Input file is empty: {input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing CSV: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Process Revolut CSV exports for reconciliation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python main.py transactions.csv
  python main.py transactions.csv -o output.csv
        """
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Input CSV file from Revolut export"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output CSV file (default: input_file with '_processed' suffix)",
        default=None
    )

    args = parser.parse_args()

    # Generate output filename if not specified
    if args.output is None:
        output_file = args.input_file.parent / f"{args.input_file.stem}_processed.csv"
    else:
        output_file = args.output

    # Process the CSV
    process_revolut_csv(args.input_file, output_file)


if __name__ == "__main__":
    main()
