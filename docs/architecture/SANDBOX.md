# NosAi Sandbox Manager

The sandbox is the execution boundary between an agent and repository code.

## Required lifecycle

`create -> execute -> collect -> destroy`

Cleanup is mandatory even when execution raises or times out.

## Security contract

The default policy is:

- isolated Git worktree;
- explicit command execution only;
- bounded execution time;
- positive CPU/memory limits represented in the contract;
- network disabled by default;
- no inherited secrets by design;
- no execution during sandbox creation;
- deterministic cleanup.

## Backends

`LocalWorktreeSandbox` is the CI/offline baseline. A Docker backend will implement
the same `SandboxProvider` contract for real agent execution. The Docker backend
must enforce network isolation, read-only base image layers where practical,
resource limits, dropped capabilities, non-root execution, and a temporary
workspace.

## Promotion boundary

A sandbox may produce patches and artifacts. It may never promote a patch to the
main branch. Promotion remains a separate Control Plane policy decision after
tests, independent verification and evaluation.
