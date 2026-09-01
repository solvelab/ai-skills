# Sea turtle

regimes: `articulated-body`
view: depends on the request. **Ask** — a turtle's flipper stroke and its body outline read from
different views, and the canonical view is genuinely ambiguous.

| fact | value | source |
|---|---|---|
| flipper twist | −73° / +35° | published kinematics — **and this is TWIST, not stroke.** Applying it as stroke hung the flippers below the shell. |
| gait | the front flippers beat TOGETHER, mirrored, not alternating | turtle swimming; this is why `verify-motion.mjs` distinguishes `-sync-near`/`-sync-far` from `-near`/`-far` |

unknown: stroke-plane amplitude in the same source's axis convention. Marked `assumed` where used.

The whole reason this dossier exists in this form: a number without its axis is not a measurement.
