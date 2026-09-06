Write the test before the code it covers. For any change with behaviour worth naming — a branch, a
parser, a boundary, a money or security path — the first artifact you write is a test that fails
for the right reason, and only then the implementation that makes it pass. A test written after the
code confirms what you already built; a test written before it decides what to build.
- The test comes first, in its own file under the project's test directory, and it names the
  behaviour the request describes — not the shape of the implementation you have in mind.
- A test that passes before the implementation exists is not a test of that behaviour: it is a test
  of nothing. Write the assertion so that the missing behaviour is what makes it fail.
- One behaviour per test, and the boundaries the request states get their own cases: the empty
  input, the inclusive or exclusive edge, the zero, the negative, the value that cannot be parsed.
- Do not grow the suite beyond the behaviour asked for. The cycle is red, then green, then tidy —
  never a suite that documents code nobody requested.
- The implementation is the smallest change that turns the failing test green, and nothing beyond it.
