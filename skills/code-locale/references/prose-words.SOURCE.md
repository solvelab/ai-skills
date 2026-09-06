# Provenance of `prose-words-pt.txt` and `prose-words-en.txt`

| Field | Value |
|---|---|
| Source | Hand-curated by the catalog maintainers, 2026-09-06 (issue #179). No external list was imported. |
| Licence | MIT, like the rest of the repository. |
| Shape | One word per line, lowercase, `#` opens a comment. Portuguese keeps its accents as typed; common unaccented spellings of the most frequent words (`nao`, `voce`, `esta`, `apos`) are listed beside the accented ones because that is how they reach a comment. |
| Size | 165 Portuguese, 170 English at the time of writing — `grep -cv '^#\|^$'` on each file is the current count. |
| Invariant | The two files share **no** word. `check-prose-locale.py` computes the intersection when it loads them and refuses to run if it is not empty; `--selftest` asserts the same. |

## What goes in

Function words only — articles, prepositions, contractions, pronouns, determiners, conjunctions,
the adverbs and auxiliaries every sentence carries — plus the handful of verbs a code comment
uses in every other line (`returns`/`retorna`, `make`/`fazer`, `pode`/`can`). Function words are
what makes the classification cheap and stable: they do not depend on the domain, they appear in
every sentence longer than a few words, and a closed list of a couple of hundred covers the bulk of
any comment. Content vocabulary (nouns, technical terms) is deliberately **out**: it is open-ended,
domain-bound, and the place where the two languages borrow from each other.

## What stays out — the ambiguity rule

A word that exists in **both** languages is evidence for neither and is excluded even when it is
the most frequent word of one of them: `a`, `as`, `no`, `do`, `me`, `sem`, `via`, `so`, `um`, `em`,
`para`, `for`, `era`, `ver`, `usa`, `num`, `ali`, `nova`, `anterior`, `logo`, `final`, `data`,
`total`, `real`, `local`, `etc`, `ok`, `note`, `come`, `alias`, `ha`. Some are true cognates
(`total`), some are collisions of unrelated words (`for` the English preposition against `for` the
Portuguese subjunctive of *ser*; `so` against the unaccented `só`; `em` against the CSS unit and
the HTML tag), and some are the names a programmer gives a variable (`i`, `x`, `num`, `val`). The
detector tolerates one stray hit — a Portuguese comment with a single English-list word is still
Portuguese — but a shared word would add a hit on **both** sides of every sentence, and that is
what the dominance rule cannot absorb.

The detector never deaccents a token before looking it up: `só` and `so` are different words in
the two files, and folding them would recreate exactly the collision the rule exists to avoid.

## How the lists were pruned

Seeded from the maintainers' own knowledge of the two languages' closed word classes, then measured
against three corpora before the first release (the numbers are in the change
`add-prose-locale-gate`, tasks S.3): a Portuguese-language service whose comments are mostly
English (`omnivoice-tts/server_addons`, every gating finding adjudicated by hand), this catalog's
skill and hook trees under a temporary `prose: en` (expected zero gating findings), and
the catalog's archived changes under `prose: pt-BR` (Portuguese prose, expected zero gating
findings). A word that produced a false positive in any of them was removed from the lists rather
than special-cased in the code.

## Adding a line

1. It must be a function word of one language, in the sense above.
2. Check it is not a word of the other language — including as an abbreviation, a loop variable,
   a unit or a proper name that reaches comments in lowercase. When in doubt, leave it out; the
   dominance rule means a missing word costs a little recall and a shared word costs precision.
3. Run `python3 check-prose-locale.py --selftest`: the intersection assertion and the calibration
   cases must stay green.
