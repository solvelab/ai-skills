"""Adversarial self-test: inject one known defect per check into a copy of the catalog
and assert the validator fires. A checker that never fails is not a checker."""
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
 "C5 no version pin": ("skills/react-api-client/SKILL.md",
     lambda s: s + "\n```tsx\n" + "const a = 1\n" * 45 + "```\n\nUses zod and vite.\n"),
 "C6 wrong tag": ("skills/r3f-materials/SKILL.md",
     lambda s: s + "\n```tsx\nvarying vec2 vUv;\nvoid main() {}\n```\n"),
}

fails = []
for check, (relpath, mutate) in MUTATIONS.items():
    with tempfile.TemporaryDirectory() as td:
        dst = pathlib.Path(td) / "repo"
        shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns(".git", "node_modules"))
        p = dst / relpath
        p.write_text(mutate(p.read_text()))
        out = subprocess.run([sys.executable, str(dst / "scripts" / "validate-skills.py")], cwd=dst, capture_output=True, text=True).stdout
        caught = check.split()[0] in out and check in out
        print(f"  {'CAUGHT ' if caught else 'MISSED '} {check}")
        if not caught:
            fails.append(check)
print(f"\n{len(MUTATIONS)-len(fails)}/{len(MUTATIONS)} defect classes detected")
sys.exit(1 if fails else 0)
