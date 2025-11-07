# Revolut Extract Generator

A Python script to process Revolut transaction CSV exports for easier reconciliation and accounting.

## Features

- Filters Revolut CSV exports to keep only relevant columns
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
uv run python main.py transactions.csv
```

This will create `transactions_processed.csv` in the same directory.

### Specify output file:
```bash
uv run python main.py transactions.csv -o output.csv
```

### Get help:
```bash
uv run python main.py --help
```

## Columns Kept

The script filters the Revolut CSV to keep only these columns:

1. Date completed (UTC)
2. Description
3. Orig currency
4. Orig amount
5. Amount
6. Balance
7. Exchange rate

## Future Enhancements

The script is designed to be easily extended with:
- Conditional column additions based on existing data
- Transaction categorization
- Data validation and cleaning
- Custom business logic

## Development

To modify which columns are kept, edit the `COLUMNS_TO_KEEP` list in `main.py`:

```python
COLUMNS_TO_KEEP = [
    "Date completed (UTC)",
    "Description",
    # Add or remove columns as needed
]
```
