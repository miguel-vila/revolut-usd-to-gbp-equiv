# Revolut Extract Generator

A Python script to transform Revolut transaction CSV exports into GBP equivalent transaction statements.

## Features

- **GBP Conversion**: Automatically converts all transactions to GBP equivalents
  - Uses daily exchange rates from Frankfurter API (European Central Bank data)
  - Smart handling: GBP transactions use original amount, others converted via USD→GBP
  - Works with multi-currency transactions (USD, EUR, COP, etc.)
- Filters Revolut CSV exports to keep only relevant columns
- Sorts transactions by date (oldest first)
- Handles missing columns gracefully with clear error messages
- Automatically generates output filename with `_processed` suffix
- Built with pandas for reliable CSV processing
- Type hints and documentation for maintainability

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install dependencies
uv sync
```

## Usage

### Basic usage (output file auto-generated):
```bash
uv run python main.py transactions.csv 1000.00
```

This will create `transactions_processed.csv` in the same directory, starting with an initial GBP balance of 1000.00.

### Specify output file:
```bash
uv run python main.py transactions.csv 1500.50 -o output.csv
```

### Get help:
```bash
uv run python main.py --help
```

## Output Columns

The script produces a clean CSV with the following columns (all numeric values rounded to 2 decimal places):

1. **date** - Transaction date
2. **description** - Transaction description
3. **amount** - Transaction amount in USD (account currency)
4. **balance** - Account balance in USD
5. **amount gbp** - Transaction amount converted to GBP

## Future Enhancements

The script is designed to be easily extended with:
- Conditional column additions based on existing data
- Transaction categorization
- Data validation and cleaning
- Custom business logic

## Modules

### main.py
Main script for processing Revolut CSV exports with column filtering and sorting.

### exchange_rate_client.py
Standalone client for fetching daily exchange rates to GBP using the Frankfurter API (European Central Bank data). Uses only Python standard library (no external dependencies).

Can be tested independently:
```bash
uv run python exchange_rate_client.py
```

## Development

To modify which columns are kept, edit the `COLUMNS_TO_KEEP` list in `main.py`:

```python
COLUMNS_TO_KEEP = [
    "Date completed (UTC)",
    "Description",
    # Add or remove columns as needed
]
```
