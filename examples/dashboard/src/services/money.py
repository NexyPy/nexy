def money(cents: int) -> str:
    """`123456` cents as `$1,234.56`."""
    return f"${cents / 100:,.2f}"
