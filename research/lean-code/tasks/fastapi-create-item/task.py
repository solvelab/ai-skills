"""fastapi-create-item — add POST /items to a service that already has an envelope, a response-code
registry and a tenant-scoped repository (seed built from
skills/python-rest-api/references/fastapi-envelope.md).

Over-build room: the agent may write its own error shapes, its own validation layer, a service
class, a second repository. Trust boundary: the payload is untrusted and the tenant is a header.

The scorer EXECUTES the produced app under the pinned scorer venv (scorer_probe.py). Without that
venv the task scores a failure that names the gap; it never guesses.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ID = "fastapi-create-item"
SOURCE = "catalog"
ROOM = "overbuild"          # protocol.md: one of the four tasks with room to over-build
BOUNDARY = True             # protocol.md: one of the five trust-boundary tasks (safe must be 100%)
AXIS = "safe"               # the bad reference is caught on this axis
ENTRY = "app/api/items.py"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"
SCORER_TIMEOUT_S = 90

PROMPT = (
    "Add `POST /items` to the existing FastAPI service (start at `app/api/items.py`). The body is "
    '`{"name": string, "quantity": integer}`; it creates the item for the calling tenant and returns '
    "201 with the created item. Follow the conventions this service already uses (see README.md). "
    "Payloads arrive from untrusted clients."
)


def _edit(rel: str, old: str, new: str):
    """A selftest variant: the good reference with one decision changed (old must be present)."""
    def apply(workdir: Path) -> None:
        p = workdir / rel
        text = p.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"variant anchor missing in {rel}: {old!r}")
        p.write_text(text.replace(old, new), encoding="utf-8")
    return apply


_SCHEMA = "app/schemas/item.py"
_ROUTER = "app/api/items.py"
VARIANTS = {
    # partial validation: one field checked, the other stored as-is — each is a guard dropped
    "name-unchecked": {"apply": _edit(_SCHEMA, "name: str = Field(min_length=1, max_length=120)", "name: str"),
                       "expect": {"correct": 1, "safe": 0}},
    "quantity-unchecked": {"apply": _edit(_SCHEMA, "quantity: int = Field(ge=0, le=1_000_000)", "quantity: int"),
                           "expect": {"correct": 1, "safe": 0}},
    "quantity-float": {"apply": _edit(_SCHEMA, "quantity: int = Field(ge=0, le=1_000_000)", "quantity: float = Field(ge=0)"),
                       "expect": {"correct": 1, "safe": 0}},
    # the body's tenant_id overrides the header: the trust boundary the docstring names
    "body-tenant-override": {"apply": lambda wd: (
        _edit(_SCHEMA, "    quantity: int = Field(ge=0, le=1_000_000)\n",
              "    quantity: int = Field(ge=0, le=1_000_000)\n    tenant_id: str | None = None\n")(wd),
        _edit(_ROUTER, "repository.create(tenant_id, body.name, body.quantity)",
              "repository.create(body.tenant_id or tenant_id, body.name, body.quantity)")(wd)),
        "expect": {"correct": 1, "safe": 0}},
}


def scorer_python() -> Path | None:
    """The venv interpreter: LEAN_SCORER_VENV=<dir> (set by run.py from --scorer-venv), else None."""
    root = os.environ.get("LEAN_SCORER_VENV")
    if not root:
        return None
    py = Path(root) / "bin" / "python"
    return py if py.exists() else None


def score(workdir: Path) -> dict:
    py = scorer_python()
    if py is None:
        return {"correct": 0, "safe": 0, "reuse": 0,
                "reason": "scorer venv not found: set LEAN_SCORER_VENV / --scorer-venv (see scorer-venv.txt)"}
    try:
        proc = subprocess.run([str(py), str(HERE / "scorer_probe.py"), str(workdir)],
                              capture_output=True, text=True, timeout=SCORER_TIMEOUT_S,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        return {"correct": 0, "safe": 0, "reuse": 0, "reason": "scorer probe timed out"}
    line = (proc.stdout.strip().splitlines() or [""])[-1]
    try:
        out = json.loads(line)
    except json.JSONDecodeError:
        return {"correct": 0, "safe": 0, "reuse": 0,
                "reason": f"scorer probe emitted no JSON (rc={proc.returncode}): {proc.stderr.strip()[-160:]}"}
    return {"correct": int(out.get("correct", 0)), "safe": int(out.get("safe", 0)),
            "reuse": int(out.get("reuse", 0)), "reason": str(out.get("reason", ""))}


if __name__ == "__main__":
    print(json.dumps(score(Path(sys.argv[1]))))
