# Revolut Extract Generator

A Python script to transform Revolut transaction (in USD) CSV exports into GBP equivalent transaction statements.

(generated with Claude Code)

## Features

- **GBP Conversion**: Automatically converts all transactions to GBP equivalents
  - Uses daily exchange rates from Frankfurter API (European Central Bank data)
  - Smart handling: GBP transactions use original amount, others converted via USD→GBP
  - Works with multi-currency transactions (USD, EUR, COP, etc.)
  - In-memory caching for exchange rates (avoids redundant API calls for same-day transactions)
- **Simple Output**: Produces clean CSV with only essential columns (date, description, amount gbp)
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

