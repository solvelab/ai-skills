"""Task money-round: half-up rounding, where Python's default is half-even.

Room to get it wrong: `round()` and the default Decimal rounding are half-even, so 2.325 becomes
2.32 instead of 2.33, and a negative half rounds the wrong way.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

ID = "money-round"
KIND = "specified"
ENTRY = "src/money.py"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"
HIDDEN_DIR = HERE / "hidden"

PROMPT = (
    "In src/money.py, implement round_money(value) so that it rounds a decimal.Decimal amount to "
    "exactly two decimal places.\n\n"
    "Use half away from zero: a half cent rounds up in absolute value, never to the nearest even "
    "digit. So 2.345 becomes 2.35, 2.325 becomes 2.33, and -2.345 becomes -2.35. A value below "
    "half rounds down: 2.344 becomes 2.34. The result always carries two decimal places, so 5 "
    "becomes 5.00 and 0 becomes 0.00."
)
