## MODIFIED Requirements

### Requirement: The catalog carries no credentials

The repository SHALL be scanned for credentials by a script wired into CI. The gate SHALL run against
the **working tree**, which can be kept clean; a separate on-demand mode SHALL report findings in the
full git history without gating, because a secret already published cannot be removed by a later
commit and a gate that can never pass is one contributors learn to ignore.

Findings that are operational detail rather than credentials — private (RFC1918) addresses, internal
hostnames — SHALL be reported distinctly and SHALL NOT fail the build.

The scanner SHALL carry a self-test, wired into CI beside the scan, that injects one credential per
pattern it claims to detect and asserts each class is reported, including a credential preceded by a
word the placeholder filter recognises and one wrapped in angle brackets, because the filter that
silences documentation placeholders SHALL apply to the matched token only and never to the text
around it. The self-test SHALL build its samples at run time rather than carry them as literals, so
the scanner's own source does not fail the scan. The pattern set SHALL cover fine-grained GitHub
tokens (`github_pat_`) and `sk-`-prefixed API keys in addition to the classic classes.

#### Scenario: A credential added to the tree fails the build

- **WHEN** a change introduces an API key, token, private key, JWT or a connection string carrying a
  password into any tracked text file
- **THEN** the CI secret scan fails and names the file and the matched class

#### Scenario: An example credential is written so it cannot be mistaken for one

- **WHEN** documentation needs to show a connection string or a secret-shaped value
- **THEN** it uses an unmistakable placeholder, so the scanner does not have to guess and a reader
  cannot copy something that looks real

#### Scenario: History is reported, not gated

- **WHEN** the history contains a finding that a later commit already removed from the tree
- **THEN** the audit mode reports it with its class, and the build is not failed by it

#### Scenario: A credential after a placeholder word is still a credential

- **WHEN** a real-shaped token is written after the word `test` (`test_token = ghp_…`) or between
  angle brackets (`<ghp_…>`)
- **THEN** the scanner reports it, because the placeholder filter is applied to the token and not to
  the forty characters before it

#### Scenario: A scanner pattern that cannot fire is caught

- **WHEN** a change to the scanner silently stops one of its patterns from matching its sample
- **THEN** `--selftest` fails naming the pattern, because a clean tree and a pattern that cannot fire
  are otherwise indistinguishable
