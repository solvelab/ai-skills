# Provenance of `english-words.txt.gz`

| Field | Value |
|---|---|
| Source | `dwyl/english-words`, file `words_alpha.txt` |
| URL | https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt |
| Licence | **Unlicense** — "This is free and unencumbered software released into the public domain." Compatible with this repository's MIT licence. |
| Taken on | 2026-08-26 |
| Upstream size | 370,105 words, 4,234,910 bytes (`content-length` of the raw file on that date) |
| Shipped here | 369,652 words — filtered to length ≥ 3, ASCII letters only, lowercased, sorted, deduplicated. The floor is 3 and not `MIN_SEGMENT` (4) on purpose: the compound rule splits `oneline` into `one` + `line`, and a list starting at 4 would break every compound whose first half is three letters. |
| Compressed size | 1,088,591 bytes, read with the standard library's `gzip` module |

## Why a bundled list and not the host's dictionary

`/usr/share/hunspell/en_US.dic` was measured on 2026-08-26 and rejected: 79,013 entries, and it does
**not** contain `read`, `input`, `context`, `math`, `detail`, `reset`, `decode` or `struct` — the file
jumps from `react/V` straight to `readability/SM`. A dictionary with holes in base words would report
`read` as a finding on the first run. The list shipped here contains all eight.

Bundling also makes the answer deterministic: the same segment produces the same verdict on a
maintainer's machine, in CI, and inside the write-time hook, with no environment to install.

## Refreshing it

The upstream list is a plain, newline-separated word file. To take a newer copy, download it, apply
the same filter (length ≥ 3, ASCII letters, lowercase, sorted, unique), write it with `gzip`, and
update the two size rows above with the numbers the download actually reported. Do not edit the
compressed file by hand — words that belong to this profession rather than to English go in
`programming-words.txt`, which is curated here and auditable on its own.
