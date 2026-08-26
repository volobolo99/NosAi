# NosAi Development Execution Protocol

## Purpose

Keep the project progressing in small, verifiable units without exhausting API/tool limits or creating large, fragile changes.

## Execution rules

1. **One block at a time.** A block has one objective and one exit gate.
2. **Batch reads.** Prefer one repository-tree or targeted file read over many small requests.
3. **Batch writes.** Group documentation/checklist changes when they belong to the same logical checkpoint. Never update the same path concurrently.
4. **No speculative dependencies.** A library enters the project only after checking purpose, maintenance, license, compatibility, footprint, and whether existing code already solves the problem.
5. **No broad refactors during foundation work.** Preserve working behavior unless the current block explicitly requires a change.
6. **Verify before advancing.** After implementation, run/inspect the smallest relevant test/CI/evaluation gate available; record failures rather than hiding them.
7. **Checkpoint after each block.** Record what changed, what was verified, remaining risks, and the exact next block.
8. **Stop on uncertainty.** If a change could affect live client control, security, data integrity, or the learning contract, isolate it into a new block instead of mixing it into unrelated work.
9. **Rate-limit aware operation.** Avoid repeated polling. Prefer cached/contextual information, targeted requests, and short sequential batches. Never intentionally hammer GitHub or CI.
10. **No false completion.** A commit is not considered verified merely because it was written successfully; CI/tests must establish the relevant gate.

## Brain expansion order

`baseline -> contracts -> strategic brain -> memory -> simulator -> RL -> perception -> planner -> guarded execution -> autonomous cycle -> optimization`

Each stage must remain usable independently. RL, vision, and live action are not prerequisites for keeping the core testable.

## Definition of Done for a block

- implementation/documentation is committed;
- relevant tests or static checks are added/updated;
- CI/evaluation status is known;
- no known regression is left unexplained;
- the next block has explicit prerequisites;
- risks and assumptions are documented.

## Recovery rule

If a block fails, create a smaller corrective sub-block. Do not repeatedly retry the same large operation. Preserve the last known-good checkpoint and resume from there.
