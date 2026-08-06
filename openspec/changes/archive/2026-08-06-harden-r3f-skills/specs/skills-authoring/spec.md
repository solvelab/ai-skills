## ADDED Requirements

### Requirement: Code blocks compile or are marked

A fenced code block tagged with a compiled or type-checked language SHALL either be a complete module
that compiles against the skill's stated stack, or carry an explicit marker identifying it as an
illustrative excerpt. A block SHALL be tagged with the language it actually contains.

#### Scenario: Excerpt is distinguishable from broken code

- **WHEN** a skill shows a fragment that is not a complete module (a bare JSX element, a partial
  function body)
- **THEN** the block carries an excerpt marker, so a reader and a compile check can both tell it apart
  from a block that is simply wrong

#### Scenario: Compilable block is verified by compiling it

- **WHEN** a skill ships a block presented as usable code in a compiled language
- **THEN** it is extracted and compiled against the declared dependency versions before publication,
  and unresolved imports or type errors are fixed rather than shipped

### Requirement: Versioned external APIs are pinned

A skill whose content targets an external API with breaking releases SHALL state the exact versions it
was verified against, and SHALL name any known upcoming rename or removal that will invalidate it.

#### Scenario: Reader can tell which era the code targets

- **WHEN** a skill documents a library API
- **THEN** the skill names the library versions its examples were verified against, rather than
  leaving the reader to infer it

#### Scenario: A known breaking change is disclosed, not silently absorbed

- **WHEN** the upstream has announced a rename or removal affecting the skill's examples
- **THEN** the skill names it and where it applies, instead of presenting the current form as timeless
