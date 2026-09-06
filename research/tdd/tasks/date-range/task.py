"""Task date-range: a half-open interval, where the natural loop writes a closed one.

Room to get it wrong: `while current <= end` reads as the obvious loop and produces one day too
many; the equal-dates case then returns one element instead of none.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

ID = "date-range"
KIND = "boundary"
ENTRY = "src/daterange.py"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"
HIDDEN_DIR = HERE / "hidden"

PROMPT = (
    "In src/daterange.py, implement date_range(start, end) so that it returns the list of "
    "datetime.date values in the interval.\n\n"
    "The interval is half-open: start is included, end is not. So from 2026-01-01 to 2026-01-04 "
    "the result is the first, the second and the third of January. When start and end are the "
    "same day the result is the empty list. The range crosses month and year boundaries normally, "
    "and it includes a leap day when the interval covers one.\n\n"
    "Raise ValueError when end is before start."
)
