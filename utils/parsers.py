"""Parsing logic for quick sale input."""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedSale:
    """Parsed sale data from quick input."""
    article: Optional[str]
    price: float
    quantity: int

    @property
    def total(self) -> float:
        return self.price * self.quantity


def parse_quick_sale(text: str) -> Optional[ParsedSale]:
    """
    Parse one of the supported quick-entry forms.

    Numeric input can be ``price quantity`` or ``quantity price``. A token
    containing a decimal separator is always treated as a price, including
    values such as ``2.0``. When both tokens are integers, the larger value is
    treated as the price. An article must be the first token and is accepted
    only together with two numeric values.
    """
    if not text or not text.strip():
        return None

    parts = ""
    if "*" in text:
        parts = text.strip().split("*")
    else:
        parts = text.strip().split()
    article: Optional[str] = None

    if _looks_like_article(parts[0]):
        article = parts.pop(0)
        if len(parts) != 2:
            # The supported article forms are ``art price quantity`` and
            # ``art quantity price``.
            return None
    elif len(parts) > 2:
        return None

    if len(parts) == 1:
        value = _parse_number(parts[0])
        if value is None or value <= 0:
            return None
        return ParsedSale(article=article, price=value, quantity=1)

    if len(parts) != 2:
        return None

    first = _parse_number(parts[0])
    second = _parse_number(parts[1])
    if first is None or second is None or first <= 0 or second <= 0:
        return None

    result = _determine_price_and_quantity(first, second, parts[0], parts[1])
    if result is None:
        return None

    price, quantity = result
    return ParsedSale(article=article, price=price, quantity=quantity)


def _looks_like_article(text: str) -> bool:
    """Return whether a token is an article rather than a number."""
    if _is_number(text):
        return False
    return bool(re.fullmatch(r"[A-Za-zА-Яа-я0-9_-]+", text))


def _is_number(text: str) -> bool:
    """Return whether text represents a finite decimal number."""
    try:
        value = float(text.replace(",", "."))
    except ValueError:
        return False
    return value == value and value not in (float("inf"), float("-inf"))


def _parse_number(text: str) -> Optional[float]:
    """Parse a decimal number using either comma or dot."""
    try:
        value = float(text.replace(",", "."))
    except ValueError:
        return None
    return value if value == value and value not in (float("inf"), float("-inf")) else None


def _determine_price_and_quantity(
    val1: float, val2: float, str1: str, str2: str
) -> Optional[tuple[float, int]]:
    """Determine price and integer quantity according to the input rules."""
    str1_has_decimal = "." in str1 or "," in str1
    str2_has_decimal = "." in str2 or "," in str2

    if str1_has_decimal and str2_has_decimal:
        # Both values are explicitly prices, so no integer quantity can be
        # determined unambiguously.
        return None

    if str1_has_decimal:
        if not _is_positive_integer(val2):
            return None
        return val1, int(val2)

    if str2_has_decimal:
        if not _is_positive_integer(val1):
            return None
        return val2, int(val1)

    # With two integers the larger value is the price.
    if val1 >= val2:
        return val1, int(val2)
    return val2, int(val1)


def _is_positive_integer(value: float) -> bool:
    """Return whether a numeric value is a positive integer."""
    return value > 0 and value.is_integer()
