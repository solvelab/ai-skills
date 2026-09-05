"""Adversarial self-test: inject one known defect per check into a copy of the catalog
and assert the validator fires. A checker that never fails is not a checker.

Each entry is  label: (relpath, mutate, expect)  — `expect` is the check name the validator must
print for that label, plus an optional fragment its finding must carry. It exists because one
check can own more than one defect class (C8 has five headings) and a dict cannot repeat a key."""
import shutil, subprocess, sys, tempfile, pathlib, re, os

SRC = pathlib.Path(__file__).resolve().parent.parent
VAL = str(SRC / "scripts" / "validate-skills.py")

MUTATIONS = {
 "C1 missing path": ("skills/fivem-lua/SKILL.md",
     lambda s: s + "\n\nSee `references/this-file-does-not-exist.md` for details.\n"),
 "C2 unknown skill": ("skills/fivem-lua/SKILL.md",
     lambda s: s + "\n\n- `fivem-teleport` — use this skill for teleport logic.\n"),
 "C3 bash syntax": ("skills/assettoserver-ops/SKILL.md",
     lambda s: s + "\n```bash\nif true then echo broken\n```\n"),
 "C3 yaml parse": ("skills/helm-migration/SKILL.md",
     lambda s: s + "\n```yaml\nfoo: [1, 2\n  bar: : baz\n```\n"),
 "C3 json parse": ("skills/claude-statusline/SKILL.md",
     lambda s: s + '\n```json\n{"a": 1,,}\n```\n'),
 "C3 python syntax": ("skills/python-rest-api/SKILL.md",
     lambda s: s + "\n```python\ndef broken(:\n    pass\n```\n"),
 "C3 lua syntax": ("skills/fivem-lua/SKILL.md",
     lambda s: s + "\n```lua\nlocal x = = 1\n```\n"),
 "C4 desc vs body": ("skills/conventional-commit/SKILL.md",
     lambda s: s.replace("description: >-", "description: >-\n  ALWAYS creates all three tiers.", 1)
                .replace("\n## ", "\n## Rules\n\nDo not create documents that don't apply.\n\n## ", 1)),
 # C5 owns three defect classes since issue #131 (2026-09-05). (a) The block stripped from a
 # code-heavy skill: nothing else in fivem-lua reads as a pin, so the literal is what fires.
 "C5 no version pin": ("skills/fivem-lua/SKILL.md",
     lambda s: s.replace("**Verified against**", "**Checked with**", 1),
     ("C5 no version pin", "neither")),
 # (b) The loose form that passed for months: strip the literal and leave "Probed on CLI 1.6.0"
 # where it is — the old regex accepted it as a pin, this one must not.
 "C5 no version pin (loose mention)": ("skills/openspec/SKILL.md",
     lambda s: s.replace("**Verified against**", "**Checked with**", 1),
     ("C5 no version pin", "mentioned in passing is not a pin")),
 # (c) The declaration on a skill whose 70+ fenced bash lines drive kubectl: the exit exists for
 # process skills, and k8s-tune-resources carries no deferral phrase. (The r3f skills keep their code
 # under references/, so their SKILL.md has zero fenced lines and would stay silent here by design.)
 "C5 no version pin (declaration on code-heavy API skill)": ("skills/k8s-tune-resources/SKILL.md",
     lambda s: s.replace("**Verified against**: `kubectl v1.36.1`",
                         "**Not version-bound**: this skill does not depend on a tool version — `kubectl v1.36.1`", 1),
     ("C5 no version pin", "declared not version-bound")),
 "C6 wrong tag": ("skills/r3f-materials/SKILL.md",
     lambda s: s + "\n```tsx\nvarying vec2 vUv;\nvoid main() {}\n```\n"),
 "C7 orphan wrapper": (None, None),
 "C8 meta section": ("skills/openspec/SKILL.md",
     lambda s: s + "\n## Trigger Test Cases\n\nShould trigger on:\n- \"do the thing\"\n"),
 # The heading that escaped C8 for months: same content as the description, read after routing.
 "C8 meta section (when-to-use heading)": ("skills/openspec/SKILL.md",
     lambda s: s + "\n## When to use this skill\n\nUse when the user asks for a proposal.\n",
     ("C8 meta section", "When to use this skill")),
 # Valid Python so C3 stays silent. The dict *value* 'endereco' is a string literal and must NOT
 # be flagged — this mutation therefore also asserts that literal stripping still works.
 "C9 identifier locale": ("skills/python-rest-api/SKILL.md",
     lambda s: s + "\n```python\ndef criar_pedido(id_usuario):\n"
                   "    return {'x': 'endereco'}\n```\n"),
 # 1100 characters of PARSED value on top of a short description: the folded scalar keeps the
 # indentation out of the count, so the padding is what the reference validator would measure too.
 "C10 frontmatter limits": ("skills/r3f-geometry/SKILL.md",
     lambda s: s.replace("description: >-", "description: >-\n  " + "Use when the user says so. " * 44, 1),
     ("C10 frontmatter limits", "description is")),
 # A reference file nobody links. The path does not exist in the catalog, so the loop below starts
 # from an empty string — this is the one mutation that CREATES a file instead of editing one.
 "C11 orphan reference": ("skills/r3f-geometry/references/orphan-probe.md",
     lambda s: "# Orphan probe\n\nNo SKILL.md and no reachable reference links this file.\n",
     ("C11 orphan reference", "orphan-probe.md")),
 # The form that shipped in six skills (issue #117): a sibling's reference path without `skills/`.
 # C1 stays silent on it by design (it only judges `references/` and `skills/` prefixes), which is
 # exactly why C12 exists.
 "C12 out-of-skill path": ("skills/fivem-lua/SKILL.md",
     lambda s: s + "\n\nThe track lives in `bug-hunter/references/track-fivem-lua.md`.\n",
     ("C12 out-of-skill path", "bug-hunter/references/track-fivem-lua.md")),
 # The same defect planted in a NESTED reference file: the per-reference loop once walked only
 # references/*.md at depth 1, and the 19 files under svg-animation/references/{objects,regimes}/
 # were judged by no path check. The fragment is the nested label, so a loop that goes back to a
 # non-recursive glob is caught even if some other file trips C12.
 "C12 out-of-skill path (nested reference)": ("skills/svg-animation/references/regimes/mechanism-linkage.md",
     lambda s: s + "\n\nThe probe lives in `research/svg-animation/probe.md`.\n",
     ("C12 out-of-skill path", "svg-animation/regimes/mechanism-linkage.md")),
 # Rule (c) in its inline form: a `..` traversal in backticks that leaves the skill. Once judged only
 # as a link target; C1 never judges `..` inline paths, so nothing else fires on it.
 "C12 out-of-skill path (inline traversal)": ("skills/r3f-geometry/SKILL.md",
     lambda s: s + "\n\nThe bindings live in `../r3f-physics/references/rapier.md`.\n",
     ("C12 out-of-skill path", "inline -> ../r3f-physics/references/rapier.md: resolves outside skills/r3f-geometry/")),
 # A description with a trigger and nothing else: no "Do NOT use", no redirect naming a sibling.
 "C13 anti-trigger clause": ("skills/r3f-physics/SKILL.md",
     lambda s: re.sub(r"description: >-\n(?:  .*\n)+",
                      "description: >-\n  React Three Fiber physics. Use when adding physics simulation.\n", s, count=1),
     ("C13 anti-trigger clause", "names no boundary")),
}

fails = []
for check, entry in MUTATIONS.items():
    relpath, mutate = entry[0], entry[1]
    expect, fragment = (entry[2] if len(entry) > 2 else (check, ""))
    with tempfile.TemporaryDirectory() as td:
        dst = pathlib.Path(td) / "repo"
        shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns(".git", "node_modules"))
        if relpath is None:                       # C7: a wrapper skill with no canonical source
            (dst / "claude" / "skills" / "ghost-skill").mkdir(parents=True)
            (dst / "claude" / "skills" / "ghost-skill" / "SKILL.md").write_text("---\nname: ghost-skill\n---\n")
        else:
            p = dst / relpath
            p.write_text(mutate(p.read_text() if p.exists() else ""))   # C11 creates its file
        out = subprocess.run([sys.executable, str(dst / "scripts" / "validate-skills.py")], cwd=dst, capture_output=True, text=True).stdout
        caught = expect.split()[0] in out and expect in out and fragment in out
        print(f"  {'CAUGHT ' if caught else 'MISSED '} {check}")
        if not caught:
            fails.append(check)
print(f"\n{len(MUTATIONS)-len(fails)}/{len(MUTATIONS)} defect classes detected")
sys.exit(1 if fails else 0)
