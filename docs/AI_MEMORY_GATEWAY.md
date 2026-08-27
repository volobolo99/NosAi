# NosAi AI + Intelligent Memory Gateway

## Decision
The OpenAI provider is isolated behind `app.ai.gateway.AIGateway`. It may advise planning, but it never authorizes or executes game actions.

## Runtime flow
Perception -> validated WorldState -> Brain/Orchestrator -> Memory context -> AI Gateway -> Decision -> deterministic Safety Gate -> proposal/action transport.

Outcomes and reward evidence flow back into NosAi-owned memory.

## Memory domains
- working: current cycle context
- episodic: prior state/action/outcome episodes
- semantic: validated game knowledge with provenance
- strategic: evaluated strategy outcomes

## Safety
Invalid/stale observation, missing decision, invalid confidence or disabled live actions must fail closed. During integration, the default is proposal-only.

## Credential boundary
`OPENAI_API_KEY` is server-side only. No key is stored in source, tests, artifacts, browser code or documentation. Live API wiring remains a separate credential-gated step.
