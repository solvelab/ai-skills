## ADDED Requirements

### Requirement: A shipped script's output is a function of its input

A skill that ships an executable which the host feeds a payload SHALL produce the same output for
the same payload. Where the output must change over time — an animation, a countdown, a freshness
indicator — the value that drives it SHALL be read from the payload rather than from the clock, the
process id, or any other ambient source.

The rule is about testability, not purity. The cheapest check that exists for such a script is to
feed it a known payload and compare the output; a render that varies on its own makes that check
report a difference that means nothing. Measured on this catalog: the status line's session
accounting was proved correct by exactly that comparison — six transcripts, six renders identical
between a cold read and a resumed cursor — and the one branch that could not participate was the
`max` effort shimmer, whose frame came from `date +%s`.

A host that advances a field on every render already supplies the clock. The status line's
`cost.total_duration_ms` is such a field: driving the animation from it keeps the animation and
returns the render to a function of its payload.

#### Scenario: an animated element in a shipped script

- **WHEN** a shipped script renders something that is meant to change between renders
- **THEN** the value driving the change is read from the payload
- **AND** SHALL NOT be read from the wall clock, the process id, or a random source

#### Scenario: the same payload twice

- **WHEN** a shipped script is fed the identical payload twice
- **THEN** the two outputs are byte-identical
- **AND** the skill's own checks may rely on that

#### Scenario: a formatted number leaves its own range

- **WHEN** a script abbreviates a number into a unit band
- **THEN** rounding never produces a value that belongs to the next band up
- **AND** SHALL NOT emit a label the function's own thresholds exclude, such as `1000k` from a
  branch whose ceiling is 1000k
