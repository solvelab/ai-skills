"""Task fix-percent-bug: an existing function with one reported crash.

Room to get it wrong: the report names ZeroDivisionError, and the cheapest patch returns 0.0 for
every zero baseline — which silently reports "no change" for a rise out of nothing. The reported
symptom and the correct behaviour differ, which is what a test written first has to pin down.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

ID = "fix-percent-bug"
KIND = "bugfix"
ENTRY = "src/percent.py"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"
HIDDEN_DIR = HERE / "hidden"

PROMPT = (
    "src/percent.py has percent_change(old, new), which reports the change from one reading to "
    "the next as a percentage of the first. A user reports that it crashes with "
    "ZeroDivisionError when the first reading is zero.\n\n"
    "Fix it. When the first reading is zero and the second is not, a percentage of zero is "
    "undefined, so raise ValueError rather than returning a number that would read as a real "
    "measurement. When both readings are zero, nothing changed, so return 0.0. Every other case "
    "keeps working exactly as it does today, including a negative first reading."
)
