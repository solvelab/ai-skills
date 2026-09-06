"""Task slug-truncate: three boundaries hidden behind an ordinary-looking helper.

Room to get it wrong: hard truncation leaves a trailing hyphen or a half word; the single-word
case and the punctuation-only case are the two an implementation written first tends to miss.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

ID = "slug-truncate"
KIND = "boundary"
ENTRY = "src/slug.py"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"
HIDDEN_DIR = HERE / "hidden"

PROMPT = (
    "In src/slug.py, implement slugify(text, max_len) so that it turns a title into a URL slug of "
    "at most max_len characters.\n\n"
    "Lowercase the text and replace every run of characters that are not a-z or 0-9 with a single "
    "hyphen, with no hyphen at either end: \"Hello,   World!!\" becomes \"hello-world\". A slug "
    "already short enough is returned unchanged.\n\n"
    "When the slug is longer than max_len, cut it at a word boundary rather than mid-word, and "
    "never return a slug that ends with a hyphen. \"the quick brown fox\" with max_len 13 becomes "
    "\"the-quick\". A text with no word characters gives the empty string, and so does a single "
    "word that is itself longer than max_len.\n\n"
    "Raise ValueError when max_len is zero or negative."
)
