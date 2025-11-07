"""
Exchange Rate Client

Fetches daily exchange rates using the Frankfurter API (ECB data).
https://frankfurter.dev/
"""

import json
import urllib.request
import urllib.error
from datetime import date, datetime
from functools import lru_cache
from typing import Optional


class ExchangeRateError(Exception):
    """Raised when exchange rate fetching fails."""
    pass


@lru_cache(maxsize=128)
def get_exchange_rate_to_gbp(currency: str, date_str: str) -> float:
    """
    Get the exchange rate from a currency to GBP for a specific date.

    Results are cached in memory to avoid redundant API calls for the same date.

    Args:
        currency: Source currency code (e.g., 'EUR', 'USD', 'JPY')
        date_str: Date in ISO format (YYYY-MM-DD)

    Returns:
        Exchange rate as a float (how many GBP per 1 unit of source currency)

    Raises:
        ExchangeRateError: If the API request fails or returns invalid data

    Example:
        >>> rate = get_exchange_rate_to_gbp('EUR', '2025-01-15')
        >>> print(f"1 EUR = {rate} GBP")
    """
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ExchangeRateError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")

    # Handle GBP to GBP (rate is always 1.0)
    if currency.upper() == "GBP":
        return 1.0

    # Build API URL
    url = f"https://api.frankfurter.dev/v1/{date_str}?base={currency.upper()}&symbols=GBP"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

            # Extract the rate from the response
            if "rates" in data and "GBP" in data["rates"]:
                return float(data["rates"]["GBP"])
            else:
                raise ExchangeRateError(f"No GBP rate found in response for {currency} on {date_str}")

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ExchangeRateError(f"No exchange rate data available for date: {date_str}")
        else:
            raise ExchangeRateError(f"HTTP error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise ExchangeRateError(f"Network error: {e.reason}")
    except json.JSONDecodeError:
        raise ExchangeRateError("Invalid JSON response from API")
    except Exception as e:
        raise ExchangeRateError(f"Unexpected error: {str(e)}")


def get_exchange_rate_to_gbp_from_date(currency: str, transaction_date: date) -> float:
    """
    Get the exchange rate from a currency to GBP for a specific date.

    Args:
        currency: Source currency code (e.g., 'EUR', 'USD', 'JPY')
        transaction_date: Python date object

    Returns:
        Exchange rate as a float (how many GBP per 1 unit of source currency)

    Raises:
        ExchangeRateError: If the API request fails or returns invalid data
    """
    date_str = transaction_date.strftime("%Y-%m-%d")
    return get_exchange_rate_to_gbp(currency, date_str)


if __name__ == "__main__":
    # Simple test
    try:
        test_date = "2025-01-15"
        test_currency = "USD"

        rate = get_exchange_rate_to_gbp(test_currency, test_date)
        print(f"✓ Exchange rate on {test_date}: 1 {test_currency} = {rate} GBP")

        # Test with GBP
        gbp_rate = get_exchange_rate_to_gbp("GBP", test_date)
        print(f"✓ Exchange rate on {test_date}: 1 GBP = {gbp_rate} GBP")

        # Test with date object
        from datetime import date
        rate2 = get_exchange_rate_to_gbp_from_date("EUR", date(2025, 1, 15))
        print(f"✓ Exchange rate on 2025-01-15: 1 EUR = {rate2} GBP")

    except ExchangeRateError as e:
        print(f"✗ Error: {e}")
