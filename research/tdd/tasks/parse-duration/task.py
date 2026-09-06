"""Task parse-duration: a parser with three units and three rejection cases.

Room to get it wrong: the spec rejects a bare number and any trailing fragment without a unit.
An implementation written without a test first tends to accept `"90"` and `"1h30"`.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

ID = "parse-duration"
KIND = "specified"
ENTRY = "src/duration.py"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"
HIDDEN_DIR = HERE / "hidden"

PROMPT = (
    "In src/duration.py, implement parse_duration(text) so that it converts a duration string "
    "into a whole number of seconds.\n\n"
    "The string is a sequence of parts. Each part is a non-negative integer immediately followed "
    "by one of the unit letters h (hours), m (minutes) or s (seconds), and the parts appear in "
    "that order. Examples: \"90s\" is 90, \"1h30m\" is 5400, \"2h3m4s\" is 7384, \"0s\" is 0.\n\n"
    "Raise ValueError for an empty string, for a number with no unit letter (\"90\"), for an "
    "unknown unit letter (\"5d\"), and for a string whose trailing characters are not part of a "
    "valid part (\"1h30\")."
)
