# Knowledge promotion gates

A source adapter produces candidates, never trusted facts. A candidate becomes
AI-readable only after schema validation, provenance validation, and conflict
checking. Client-facing semantics additionally require live validation.

The repository manifest currently classifies NosCore as the primary packet-schema
reference and NosSmooth/PacketLogger as secondary references. fileciteturn257file0L1-L7

Conflicting candidates are quarantined rather than resolved heuristically. This
keeps uncertain online information out of the decision layer while preserving it
for later validation.
