# NosCore schema import

The adapter accepts only schema data already obtained from a pinned NosCore.Packets source.
It preserves the declared schema verbatim and records source reference/commit.

It intentionally does **not** infer game semantics. For example, a field named
`Hp` is not promoted to a canonical health field merely because of its name. A
semantic mapping requires a verified schema/reference and can then be represented
as a separate mapping record.

This keeps the packet catalog lossless and prevents guessed fields from entering
the decision layer.
