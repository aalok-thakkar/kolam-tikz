# Contributing

Thank you for helping improve `kolam-tikz`.

## Before opening a change

- Keep the public input language coordinate-first: declare pulli and
  cardinal gates rather than hand-drawn repair strokes.
- Preserve the distinction between the general decorative grammar and the
  optional Drop-Fan sublanguage.
- Add an explicit example when changing the rendered vocabulary.
- Update the grammar or API reference whenever the public commands change.

Run the full local check from the package root:

```sh
make verify
```

This builds every example, checks the advertised port-graph certificates, runs
the auditor regression tests, and compiles a TikZ `\foreach` smoke test.

## Style and scope

Use the `kolam grid` TikZ style and uniform `scale=<factor>` for published
motifs. Avoid changing `x` and `y` independently: physical arc radii and
coordinate spacing must remain synchronized.

Please describe pulli kolam with care. This package offers a deliberately
narrow formal drawing language; it is not a claim to encode the full living
practice or all regional vocabularies of kolam.
