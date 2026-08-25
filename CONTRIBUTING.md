# Contributing to NosAi

## Core rule

During the repository migration, **do not change runtime behavior as part of structural work**.

## Workflow

1. Start from `main`.
2. Create a focused branch for one logical change.
3. Keep commits small and descriptive.
4. Add or update tests when behavior changes.
5. Run the full regression suite before opening a PR.
6. Include benchmark evidence for performance-sensitive changes.

## Review expectations

A change is ready for review when:

- the purpose is clear;
- the affected files are limited to the intended scope;
- tests pass;
- no generated artifacts are committed;
- compatibility impact is documented;
- performance claims are backed by measurements.

## Migration rule

The release ZIP is treated as the current baseline until the source-first tree has been verified against it. Historical documents are preserved until their role is understood.
