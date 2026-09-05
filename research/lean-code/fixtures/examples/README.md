# fixtures/examples

Eleven before/after transcripts copied verbatim from `examples/*.md` of
[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) at commit `974d940a`
(v4.9.0, MIT — licence and per-file sha256 in `../../vendor/ponytail/PIN`).

They are **selftest fixtures for the LOC counter**, nothing else. Each file has a
`## Without Ponytail` section and a `## With Ponytail` section; `run.py --selftest` counts the
fenced code of each section with the Python port and with the upstream `loc.js` under node, and
requires:

- port == `loc.js` on all 22 sections;
- `Without > With` on all 11 files.

The numbers in the headings ("75 lines of code") are the upstream's own and are not checked: the
`Without` sections carry sub-headings with more code than the heading counted, and what matters
here is that two counters agree on the same text, not that the heading was right.

Nothing here is a measurement of this catalog. The upstream produced these with Haiku 4.5 through
`promptfoo`, single-shot, chat output — the very metric it later retracted in favour of `git diff`.
