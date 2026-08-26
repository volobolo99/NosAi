# NosTale strategy model

This document records how the attached `Guida Strategica e Analisi NosTale.pdf` is being converted into explicit NosAi model inputs. It is a **source-derived engineering model**, not a claim that every formula in the PDF has been independently verified against the live Gameforge client.

## State model

The source proposes normalized inputs including HP/MP ratio, Dignity, attack/defense grade differential, effective resistance reduction, target net resistance, target distance/type, remaining instance time, hardcore raid lives and accumulated boss damage. These are represented by `app.nostale.strategy.NosTaleState`.

## High-value strategic signals

1. **Elemental resistance threshold** — the source describes 100% net elemental resistance as a hard threshold where elemental damage becomes zero. NosAi therefore exposes `resistance_break_critical` when `target_resist_net >= 1.0` rather than burying this assumption in a model weight.
2. **Dignity guard** — the source identifies `-400` as an important functional boundary. NosAi exposes `dignity_guard` below that boundary so planning can trade immediate reward against future capability/economic penalties.
3. **Room objective** — kill-all, survival, target elimination, switch access and escort rooms receive explicit objective labels. This allows the planner to select a strategy before learning a low-level action policy.
4. **Hardcore raid risk** — a low shared life pool increases the risk signal. The model keeps contribution and life preservation as separate state fields so a future policy can optimize both instead of collapsing them into one reward.
5. **Reward provenance** — generated reward metadata records the PDF as the source basis. This makes later validation and replacement of hypotheses possible without silently changing the model.

## Action-policy implications

The source proposes four action families: movement, skill selection, consumables and target selection. The current repository keeps the real-client boundary observation-only; these strategy signals therefore feed offline planning/evaluation first. Live action transport remains separately gated by the existing client-adapter architecture.

## Validation rule

Whenever live observations contradict a source-derived rule, the rule should be marked as a hypothesis, its confidence lowered in the knowledge layer, and the observed evidence retained as an episodic/evaluation record. Do not silently rewrite historical observations to match the PDF.
