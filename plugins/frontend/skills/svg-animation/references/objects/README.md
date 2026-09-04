# Object dossiers

A dossier is **thin and citable**: the facts about one object that a regime schema asks for, each
with its source, plus what is still unknown. Fifteen to thirty lines. It is written when the object
is first built, never in advance — that is what makes this scale. The number of regimes is small
and stable; dossiers grow one at a time and cost almost nothing.

Format:

```
# <object> (<Latin name if it has one>)
regimes: <which schemas apply, and to what>
view: <the canonical view, and why>
<a table of facts, each with a source>
unknown: <what was looked for and not found>
```

A number with no source is marked `assumed` and says so. A dossier that would need an invented
number stops at the gap instead.

## Existing dossiers

| Dossier | Object | Regimes |
|---|---|---|
| `broadleaf-tree.md` | Broadleaf tree | `growth-structure` (geometry) + `driven-oscillator` (motion) |
| `cumulus.md` | Fair-weather cumulus | `advected-field` |
| `herring-gull.md` | Herring gull (*Larus argentatus*) | `articulated-body` (wing) + a steered trajectory |
| `night-sky.md` | Night sky | `radiant-point-set` |
| `ocean.md` | Open ocean | `dispersive-wave-field` |
| `rain.md` | Rain | `ballistic-ensemble` |
| `sea-turtle.md` | Sea turtle | `articulated-body` |
| `walking-human.md` | Walking human | `articulated-body` |

A new dossier is added to this table when it is written.
