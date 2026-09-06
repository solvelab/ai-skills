#!/usr/bin/env python3
"""Lexical routing simulation for the lean-code description (item #146, S.1 offline part).

For each prompt, every `skills/*/SKILL.md` description is scored by
(quoted-phrase hits * 3) + content-bigram overlap + content-unigram overlap / 4, and the top two
are printed. The real router is the model; this only measures whether the lexical signal the
description carries for these prompts exists and does not collide with a sibling's. Ported from the
scratch script of issue #122 (description trims) with the prompt set of #146: three prompts that
should route to lean-code and three that must not.

KNOWN LIMIT: a lexical score is not the model's choice. A prompt that wins here can still lose in a
session, and the reverse; the interactive session in tasks.md S.6 is the measurement that counts.

Usage: python3 research/lean-code/route-sim.py   (from the repository root; needs PyYAML)
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

STOP = set("the a an of to for in on is it or and with when that this your my our do not use for from by as at be can".split())

PROMPTS = {
    "lean-code": [
        "faz o mais simples que funciona pra esse endpoint, sem inventar camada",
        "review this diff for over-engineering — what can we delete, is this over-engineered?",
        "add a cache for these API responses",
    ],
    "verify-before-claiming": [
        "isso é achismo — de onde tirou essa flag? não inventa, pesquisa antes",
    ],
    "api-resilience-testing": [
        "break this endpoint with adversarial tests: negative testing, fuzz the payloads, check the status codes",
    ],
    "documentation": [
        "prune the README: write the docs so only the pages the project earns stay, document this",
    ],
}


def descriptions() -> dict[str, str]:
    out: dict[str, str] = {}
    for d in sorted(pathlib.Path("skills").iterdir()):
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8")
        out[d.name] = yaml.safe_load(text.split("---", 2)[1])["description"]
    return out


def words(s: str) -> list[str]:
    return [w for w in re.findall(r"[\wáéíóúãõâêôç#/.<>-]+", s.lower()) if w not in STOP and len(w) > 2]


def score(prompt: str, desc: str) -> tuple[float, int, int, int]:
    p = prompt.lower()
    quoted = [q.lower() for q in re.findall(r'"([^"]+)"', desc)]
    qh = sum(1 for q in quoted if q in p)
    pw, dw = words(prompt), words(desc)
    dset, dbi = set(dw), set(zip(dw, dw[1:]))
    uni = sum(1 for w in pw if w in dset)
    bi = sum(1 for b in zip(pw, pw[1:]) if b in dbi)
    return qh * 3 + bi + uni / 4, qh, bi, uni


def main() -> int:
    descs = descriptions()
    n = ok = 0
    lean_wins_non_lean = 0
    for intended, prompts in PROMPTS.items():
        for prompt in prompts:
            n += 1
            ranked = sorted(((score(prompt, d), s) for s, d in descs.items()), reverse=True)[:3]
            top = ranked[0][1]
            ok += top == intended
            if intended != "lean-code" and top == "lean-code":
                lean_wins_non_lean += 1
            print(f"[{intended}] {prompt[:78]}")
            for (sc, qh, bi, uni), name in ranked:
                print(f"   {name:26} score={sc:.2f} quoted={qh} bigrams={bi} unigrams={uni}")
    print(f"\nprompts={n}  intended-top={ok}/{n}  descriptions={len(descs)}  "
          f"lean-code stole a non-lean prompt: {lean_wins_non_lean}/{n - len(PROMPTS['lean-code'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
