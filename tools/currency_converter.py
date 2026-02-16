"""Currency Converter Tool — uses the free ExchangeRate-API for live rates."""

import requests
from langchain_core.tools import tool


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert an amount from one currency to another using live exchange rates.

    Args:
        amount: The monetary amount to convert (e.g. 100.0).
        from_currency: Source currency code, e.g. 'USD', 'EUR', 'INR'.
        to_currency: Target currency code, e.g. 'INR', 'JPY', 'GBP'.

    Returns:
        A formatted string showing the converted amount and exchange rate.
    """
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    try:
        # Free API: https://open.er-api.com/v6/latest/{base}
        url = f"https://open.er-api.com/v6/latest/{from_currency}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("result") != "success":
            return f"Failed to fetch exchange rates for {from_currency}."

        rates = data.get("rates", {})
        if to_currency not in rates:
            return f"Currency '{to_currency}' not found. Available currencies include: {', '.join(list(rates.keys())[:20])}..."

        rate = rates[to_currency]
        converted = round(amount * rate, 2)

        return (
            f"💱 Currency Conversion:\n"
            f"  {amount:,.2f} {from_currency} = {converted:,.2f} {to_currency}\n"
            f"  Exchange Rate: 1 {from_currency} = {rate} {to_currency}\n"
            f"  Last Updated: {data.get('time_last_update_utc', 'N/A')}"
        )

    except requests.RequestException as e:
        return f"Error fetching exchange rates: {e}"
    except Exception as e:
        return f"Unexpected error in currency converter: {e}"


@tool
def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    """
    Get the current exchange rate between two currencies.

    Args:
        from_currency: Source currency code (e.g. 'USD').
        to_currency: Target currency code (e.g. 'EUR').

    Returns:
        The current exchange rate as a string.
    """
    return convert_currency.invoke({
        "amount": 1.0,
        "from_currency": from_currency,
        "to_currency": to_currency
    })


# Export tool list for the agent
currency_tools = [convert_currency, get_exchange_rate]
