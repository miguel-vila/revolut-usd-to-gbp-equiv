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
import numpy as np

from exchange_rate_client import get_exchange_rate_to_gbp, ExchangeRateError


# Columns to keep from the original Revolut CSV
COLUMNS_TO_KEEP = [
    "Date completed (UTC)",
    "Description",
    "Orig currency",
    "Orig amount",
    "Amount",
    "Balance",
]


def calculate_gbp_amount(row) -> float:
    """
    Calculate the GBP equivalent amount for a transaction.

    Logic:
    - If Orig currency is GBP: Use Orig amount with sign from Amount
    - Otherwise: Convert USD Amount to GBP using exchange rate for that date

    Args:
        row: A pandas Series representing a transaction row

    Returns:
        The transaction amount in GBP
    """
    orig_currency = row["Orig currency"]
    orig_amount = row["Orig amount"]
    amount = row["Amount"]
    transaction_date = row["Date completed (UTC)"]

    # Case 1: Transaction originally in GBP
    if orig_currency == "GBP":
        # Use the original GBP amount, but apply the sign from Amount
        # This handles currency exchanges where signs may differ
        if amount >= 0:
            return abs(orig_amount)
        else:
            return -abs(orig_amount)

    # Case 2: Transaction in any other currency (USD, COP, EUR, etc.)
    # Amount is already in USD, so convert USD to GBP
    try:
        # Convert date to string format YYYY-MM-DD
        date_str = transaction_date.strftime("%Y-%m-%d")
        usd_to_gbp_rate = get_exchange_rate_to_gbp("USD", date_str)
        return amount * usd_to_gbp_rate
    except ExchangeRateError as e:
        print(f"Warning: Could not fetch exchange rate for {date_str}: {e}", file=sys.stderr)
        print(f"  Using 0.0 for Amount GBP. Please check this transaction manually.", file=sys.stderr)
        return 0.0


def process_revolut_csv(input_file: Path, output_file: Path, initial_balance_gbp: float) -> None:
    """
    Process Revolut CSV export, transforming to GBP equivalent statement.

    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
        initial_balance_gbp: Initial GBP balance for the statement
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
        df_filtered = df[COLUMNS_TO_KEEP].copy()

        # Convert date column to datetime for proper sorting
        df_filtered["Date completed (UTC)"] = pd.to_datetime(df_filtered["Date completed (UTC)"])

        # Sort by date, oldest first
        df_filtered = df_filtered.sort_values("Date completed (UTC)", ascending=True)

        # Calculate GBP amount for each transaction
        print("Calculating GBP amounts...")
        df_filtered["Amount GBP"] = df_filtered.apply(calculate_gbp_amount, axis=1)

        # Round numeric columns to 2 decimal places
        df_filtered["Amount"] = df_filtered["Amount"].round(2)
        df_filtered["Balance"] = df_filtered["Balance"].round(2)
        df_filtered["Amount GBP"] = df_filtered["Amount GBP"].round(2)

        # Select only the columns we want in the output
        output_columns = ["Date completed (UTC)", "Description", "Amount", "Balance", "Amount GBP"]
        df_output = df_filtered[output_columns].copy()

        # Rename columns to lowercase format
        df_output.columns = ["date", "description", "amount", "balance", "amount gbp"]

        # TODO: Use initial_balance_gbp for GBP balance calculations in future iterations

        # Write to output file
        df_output.to_csv(output_file, index=False)

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
        description="Transform Revolut CSV exports to GBP equivalent statements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python main.py transactions.csv 1000.00
  python main.py transactions.csv 1500.50 -o output.csv
        """
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Input CSV file from Revolut export"
    )

    parser.add_argument(
        "initial_balance",
        type=float,
        help="Initial GBP balance for the statement"
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
    process_revolut_csv(args.input_file, output_file, args.initial_balance)


if __name__ == "__main__":
    main()
