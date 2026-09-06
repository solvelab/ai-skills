Before writing a line, climb the ladder and stop at the first rung that holds: does this need to exist at all → already in this codebase → stdlib → native platform feature → already-installed
dependency → one line → only then the minimum code that works. The ladder runs after the problem is understood, never instead of it.
- A bug report names a symptom: grep every caller and put one guard where all callers route through; patching only the named path leaves the siblings broken.
- No interface with one implementation, no factory for one product, no config for a value that never changes, no scaffolding "for later".
- A deliberate simplification carries `# lean: <ceiling> -> <upgrade trigger>`; every delivery ends with `skipped: [X], add when [Y]`.
- Never simplified away: validation at a trust boundary, error handling that prevents data loss, security, accessibility, anything explicitly requested, the calibration knob of a physical constant, and the one runnable check behind non-trivial logic. Lean is about what exists afterwards, not about speed — it never overrides best long-term outcome.
- Questioning whether a requested piece needs to exist is a line under *Assumptions* in the Doing / Not doing / Assumptions block, never a silent omission; the user decides, and "build the full version" ends the argument.
- Full doctrine, the review lens and the ledger: the `lean-code` skill.
