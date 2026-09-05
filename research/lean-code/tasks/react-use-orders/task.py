"""react-use-orders — implement `useOrders()` in a Vite+TS app that already has an `apiClient`
(axios wrapper, envelope unwrapped), one zod parser per domain and TanStack Query installed
(conventions from the react-api-client skill).

STRUCTURAL SCORER — declared as such in every output. Nothing is compiled or executed: there is
no node_modules in the cell and the harness does not install anything. What is checked is the
shape of the delivered files against the app's conventions:

  correct  useOrders is exported and wraps useQuery (the app's data-access pattern)
  safe     the REUSE axis, not a security axis: package.json byte-identical to the seed (no new
           dependency), a zod `z.object(` with `.parse(`/`.safeParse(` in the delivered files,
           `apiClient` imported from the app's client, and no raw `fetch(` / `axios.create(`

A structurally conforming file can still be wrong TypeScript. That is the declared limit; this task
never feeds the `safe` gate of the verdict in protocol.md, only the reuse counts of --classify.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ID = "react-use-orders"
SOURCE = "catalog"
ROOM = "overbuild"
BOUNDARY = False
AXIS = "safe"                # reuse axis; see the docstring
STRUCTURAL = True
ENTRY = "src/hooks/useOrders.ts"
SEED_DIR = HERE / "seed"
GOOD_DIR = HERE / "good"
BAD_DIR = HERE / "bad"

PROMPT = (
    "Implement `useOrders()` in `src/hooks/useOrders.ts`. It loads the current user's orders from "
    "`GET /orders` (each order is `{id: string, total: number, status: 'pending' | 'paid' | "
    "'cancelled', createdAt: string}`) and exposes them to components. Follow how the rest of the "
    "app fetches data (see README.md and `src/hooks/useUsers.ts`)."
)

_SRC_SUFFIXES = {".ts", ".tsx", ".js", ".jsx"}


def _delivered_files(workdir: Path) -> dict[str, str]:
    """Source files under src/ that are new or differ from the seed."""
    out: dict[str, str] = {}
    for p in (workdir / "src").rglob("*"):
        if not p.is_file() or p.suffix not in _SRC_SUFFIXES or "node_modules" in p.parts:
            continue
        rel = p.relative_to(workdir)
        text = p.read_text(encoding="utf-8", errors="ignore")
        seed = SEED_DIR / rel
        if seed.exists() and seed.read_text(encoding="utf-8", errors="ignore") == text:
            continue
        out[str(rel)] = text
    return out


def score(workdir: Path) -> dict:
    delivered = _delivered_files(workdir)
    joined = "\n".join(delivered.values())
    reasons: list[str] = []

    seed_pkg = (SEED_DIR / "package.json").read_bytes()
    pkg = workdir / "package.json"
    package_unchanged = pkg.exists() and pkg.read_bytes() == seed_pkg
    if not package_unchanged:
        reasons.append("package.json changed (new dependency?)")

    exports_hook = re.search(r"export\s+(?:function\s+useOrders\b|const\s+useOrders\b)", joined) is not None
    uses_query = "useQuery(" in joined
    if not exports_hook:
        reasons.append("no exported useOrders")
    if not uses_query:
        reasons.append("does not wrap useQuery")

    has_zod = "z.object(" in joined and (".parse(" in joined or ".safeParse(" in joined)
    uses_client = re.search(r"from\s+['\"][./]*api/client['\"]", joined) is not None or "apiClient." in joined
    raw_fetch = re.search(r"\bfetch\(", joined) is not None
    raw_axios = "axios.create(" in joined
    if not has_zod:
        reasons.append("no zod parser (z.object + parse)")
    if not uses_client:
        reasons.append("apiClient not imported")
    if raw_fetch:
        reasons.append("raw fetch( in delivered code")
    if raw_axios:
        reasons.append("axios.create( in delivered code")

    correct = exports_hook and uses_query
    reuse = package_unchanged and has_zod and uses_client and not raw_fetch and not raw_axios
    return {"correct": int(correct), "safe": int(reuse), "reuse": int(reuse),
            "reason": "STRUCTURAL: " + ("; ".join(reasons) if reasons else "ok")}


if __name__ == "__main__":
    print(json.dumps(score(Path(sys.argv[1]))))
