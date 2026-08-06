## ADDED Requirements

### Requirement: The catalog carries no credentials

The repository SHALL be scanned for credentials by a script wired into CI. The gate SHALL run against
the **working tree**, which can be kept clean; a separate on-demand mode SHALL report findings in the
full git history without gating, because a secret already published cannot be removed by a later
commit and a gate that can never pass is one contributors learn to ignore.

Findings that are operational detail rather than credentials — private (RFC1918) addresses, internal
hostnames — SHALL be reported distinctly and SHALL NOT fail the build.

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
