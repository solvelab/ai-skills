"""Task chunk-list: the trivial happy path plus two rejection boundaries.

Room to get it wrong: a non-positive size is the only way this function can misbehave, and an
implementation written without a test first tends to return [] or loop rather than raise.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

ID = "chunk-list"
KIND = "boundary"
ENTRY = "src/chunk.py"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"
HIDDEN_DIR = HERE / "hidden"

PROMPT = (
    "In src/chunk.py, implement chunk(items, size) so that it splits a list into consecutive "
    "chunks of at most `size` elements.\n\n"
    "The chunks appear in the original order and the last one may be shorter than the others: "
    "[1,2,3,4,5] with size 2 gives [[1,2],[3,4],[5]]. An empty list gives an empty list. A size "
    "larger than the list gives one chunk with everything. The input list is never mutated.\n\n"
    "Raise ValueError when size is zero or negative."
)
