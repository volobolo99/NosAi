# NosAi — GuardAi Progression Market Advisor

> Status: architecture/design
> Owner: GuardAi
> Supporting intelligence: PlayAi
> Safety authority: Decision Fabric / Safety Gate

## 1. Purpose

Add a Dashboard capability that evaluates whether an external purchase of game currency/items would materially improve a character's progression, while keeping the feature advisory-only.

The component must not automate purchases, payments, account transfers, credential sharing, or in-game delivery. It must explicitly surface publisher/game-rule compatibility before presenting any positive recommendation.

## 2. Why GuardAi owns this feature

PlayAi owns gameplay goals and progression planning. GuardAi owns:

- independent verification of the progression claim;
- opportunity-cost analysis;
- risk assessment;
- market-data quality checks;
- price/value comparison;
- uncertainty/confidence;
- compliance warnings;
- final recommendation wording.

PlayAi supplies the target progression state and estimates the in-game value of resources. GuardAi challenges that estimate and determines whether the recommendation is robust.

## 3. Critical NosTale compliance rule

Current official NosTale/Gameforge rules state that buying or selling Gold/items for other currencies, including real-world currency, is prohibited unless expressly permitted by Gameforge. The NosTale team states that violations can result in permanent bans. Current game rules also prohibit unauthorized third-party software, bots, hacks, macros, sandboxes and IP-masking services.

Therefore the NosAi feature must NOT present third-party real-money Gold/item purchases as a normal safe progression recommendation for the official Gameforge service.

The UI must instead show a prominent compatibility status:

- `PROHIBITED / HIGH ACCOUNT RISK` when current official rules prohibit the transaction;
- `ALLOWED / OFFICIAL` only when an official source confirms it;
- `UNKNOWN / VERIFY` when the rule cannot be established from an authoritative source.

The system may still analyze market information as research and may compare it against legitimate in-game acquisition routes, but it must not facilitate a prohibited transaction.

## 4. G2G integration assessment

The supplied repository `g2g-official/open-api-sample` is a public Postman collection for G2G OpenAPI. Its README describes it as a sample for getting products and creating/updating offers. The current G2G documentation describes seller-side offer/inventory management, and the API documentation currently exposes product/offer/order/inventory/store/log flows.

Important limitation: this sample is not a buyer-side NosTale Gold purchasing API. The current G2G OpenAPI documentation also states that API support is limited by product category and access requires permission/review. Therefore NosAi must NOT treat this repository as a supported purchase API.

Reusable architectural ideas:

- service → category → product → attributes hierarchy;
- offer normalization;
- price/currency fields;
- delivery metadata;
- seller/offer identifiers;
- availability/inventory;
- timestamps;
- webhook/event concepts;
- explicit API/provider adapters.

The G2G sample must be treated as reference material, not as permission to automate purchasing.

## 5. Market Intelligence Adapter

Create a technology-neutral interface:

```text
MarketProvider
  ├── discover_products()
  ├── search_offers()
  ├── normalize_offer()
  ├── get_price_history()
  ├── get_availability()
  └── get_provider_policy()
```

Initial providers for research:

1. G2G
2. PlayerAuctions
3. Other marketplaces discovered and approved by the Cloud/Research service

Do not scrape or automate a site where its terms prohibit it. Prefer official APIs, public feeds, or permitted pages.

## 6. Character Progression Model

PlayAi should expose a read-only progression snapshot:

```text
CharacterSnapshot
├── server/region
├── level / progression tier
├── class/build
├── specialist progression
├── equipment quality
├── upgrade levels
├── relevant resources
├── quest/raid unlock state
├── PvE/PvP goals
├── current bottleneck
├── current in-game earning rate
└── target milestone
```

No credentials, passwords, session tokens or account secrets are required.

## 7. Purchase Utility Engine

GuardAi evaluates each candidate resource through:

```text
Candidate Resource
       ↓
Legality / Policy Check
       ↓
Market Quality Check
       ↓
Price Normalization
       ↓
Character Bottleneck Match
       ↓
Progression Gain Estimate
       ↓
Time Saved Estimate
       ↓
Alternative In-Game Route
       ↓
Risk / Uncertainty
       ↓
Value Score
```

The engine must distinguish:

- direct progression benefit;
- indirect benefit;
- convenience only;
- cosmetic/no progression benefit;
- negative/low-value purchase;
- insufficient evidence.

## 8. Opportunity-cost model

Do not optimize only for the lowest marketplace price.

Calculate:

```text
cash_cost
estimated_in_game_value
estimated_time_saved
estimated_time_to_farm_legitimately
progression_delta
risk_penalty
uncertainty_penalty
```

A useful research metric is:

`progression_value_per_euro = expected_progression_delta / cash_cost`

and, for legitimate alternatives:

`time_saved = legitimate_route_time - alternative_route_time`

These are estimates and must always display confidence and data age.

## 9. Recommendation states

GuardAi should produce one of:

- `DO_NOT_RECOMMEND` — prohibited, unsafe or poor value;
- `NOT_USEFUL` — legal/allowed but little progression impact;
- `POSSIBLE_VALUE` — measurable benefit but significant uncertainty;
- `HIGH_VALUE_IF_ALLOWED` — strong modeled benefit, but only if the official rules permit it;
- `OFFICIAL_OPTION_RECOMMENDED` — verified official purchase route;
- `INSUFFICIENT_DATA` — not enough reliable information.

For current official NosTale/Gameforge rules, third-party real-money Gold/item purchases must resolve to `DO_NOT_RECOMMEND` unless an authoritative rule change establishes otherwise.

## 10. Dashboard design

Add a `Progression Advisor` card in the main Dashboard.

### Character state

Show:

- current progression;
- primary bottleneck;
- target milestone;
- estimated legitimate path;
- confidence.

### Market intelligence

Show, for research purposes:

- provider;
- offer category;
- normalized price;
- availability;
- seller reputation signals where legally/publicly available;
- data age;
- source link;
- policy status.

### Recommendation

Show:

```text
GuardAi recommendation
Status: DO NOT RECOMMEND
Reason: current official NosTale rules prohibit RMT Gold/item trading.
Progression impact if it were permitted: estimated X
Legitimate alternative: Y
Confidence: Z%
```

The actual UI should not encourage a prohibited purchase through ranking, checkout shortcuts or persuasive language.

## 11. Three-tier comparison

For markets/services where use is permitted, the Dashboard can compare:

- `FREE / NO-SPEND` — legitimate in-game route;
- `ECONOMY` — lowest-cost permitted external/official option;
- `PRO` — highest-capability permitted option.

For official NosTale under the current rules, the first tier should dominate because third-party Gold/item RMT is prohibited.

## 12. Forecasting and simulation

GuardAi should simulate:

### Scenario A — no external spend
Expected progression over 1d / 7d / 30d.

### Scenario B — permitted resource purchase
Only if policy check passes.

### Scenario C — alternative permitted purchase
Compare official/allowed routes.

Outputs:

- probability of reaching target;
- expected time-to-target;
- expected progression gain;
- cost;
- uncertainty interval;
- bottleneck removed/not removed.

## 13. Continuous research

A scheduled research job should refresh provider data and game-policy sources.

Recommended cadence:

- policy/rule source: daily or on detected change;
- market prices: several times per day where permitted;
- provider metadata: daily;
- historical trend aggregation: daily;
- full provider discovery: weekly.

Every recommendation must store source timestamps and evidence references.

## 14. Risk controls

Never store or request:

- game passwords;
- 2FA codes;
- marketplace passwords;
- payment card data;
- payment credentials;
- seller credentials.

Never automate:

- checkout;
- payment;
- account buying/selling;
- transfer of game accounts;
- external trade execution;
- in-game delivery.

The system may open an external source page for user inspection where appropriate, but the transaction remains outside NosAi.

## 15. Evaluation metrics

GuardAi should be evaluated on:

- progression prediction accuracy;
- price normalization accuracy;
- policy classification accuracy;
- stale-data detection;
- false-positive recommendation rate;
- false-negative recommendation rate;
- time-to-target estimation error;
- benefit estimation error;
- market-provider availability;
- recommendation reproducibility.

A critical metric is:

`unsafe_recommendation_rate = prohibited/unsafe positive recommendations / total recommendations`

Target: effectively zero.

## 16. Roadmap gates

### Market Intelligence Gate
- provider adapters defined;
- G2G schema mapping documented;
- policy metadata captured;
- no purchase automation.

### Progression Advisor Gate
- CharacterSnapshot available;
- bottleneck model validated;
- legitimate baseline modeled;
- confidence and uncertainty displayed.

### GuardAi Recommendation Gate
- independent GuardAi review;
- policy check before utility scoring;
- prohibited RMT blocked from positive recommendation;
- audit trail generated.

### Dashboard Gate
- recommendation card;
- source links;
- data freshness;
- explanation;
- alternatives;
- user remains in control.

## 17. Current conclusion

The requested G2G OpenAPI sample is useful as an architectural reference for a normalized marketplace adapter, but it should not be wired into NosAi as a purchase mechanism.

For official Gameforge NosTale, the current rules make third-party real-money Gold/item purchases a prohibited activity. Therefore the production feature should be a **GuardAi Progression & Market Intelligence Advisor**, not a purchasing agent.

Its value is still high: it can tell the player whether a resource would solve the character's actual bottleneck, quantify the expected progression benefit, compare it with legitimate in-game alternatives, monitor market/policy changes, and explain the decision with evidence — while refusing to facilitate a prohibited transaction.
