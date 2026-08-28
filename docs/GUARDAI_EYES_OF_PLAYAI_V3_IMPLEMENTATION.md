# GuardAi / EYES OF PLAYAI v3.0 — Implementation

This branch implements the source-grounded v3.0 master specification supplied for NosAi 4.21.0.

## Runtime topology

`Windows Host / NosAi -> DXGI -> NVENC -> WebRTC media -> Realme X50 Pro`

`Windows Host / PerceptionFrame -> Protobuf DataChannel (unordered/unreliable) -> Realme`

`Realme telemetry -> Room WAL -> asynchronous batch persistence`

`Windows replay telemetry -> DuckDB OLAP`

The signaling WebSocket is control-plane only. It is not a streaming or high-frequency telemetry transport.

## Isolation and fail-closed behavior

- Realme pairing requires the exact device id `REALME_X50_PRO_GUARD`.
- SDP/ICE forwarding is denied before pairing authentication.
- A Realme signaling disconnect emits `SIGNAL_LOST_FORCE_OFFLINE` to the host.
- The host hardware video source fails closed when a native DXGI/NVENC implementation is absent.
- The repository remains observation/read-only with respect to live NosTale actions; this feature does not introduce an action transport.

## PTS synchronization

`PerceptionFrame.presentation_timestamp_us` is the canonical synchronization key. The Android overlay indexes telemetry by this value and receives the decoded WebRTC frame timestamp through the video sink bridge. The native host capture/encoder adapter must preserve the source presentation timestamp through the media path; no heuristic nearest-frame matching is introduced.

## Human-in-the-loop

A touch is accepted only when it geometrically collides with a BoundingBox belonging to the frame currently selected by PTS. The gesture layer cycles `FAST`, `SMART`, `DEEP`, and `LOW_RES` and delegates the profile change to the host Mission Utility Score solver.

## Storage

DuckDB is local replay analytics storage. Android Room uses WAL and accumulates telemetry for a 60-second asynchronous batch. No Supabase/cloud call is placed on the media or telemetry hot path.

## Hardware validation gate

The code establishes the contracts and native integration boundaries. Sub-15ms latency, actual DXGI/NVENC zero-copy operation, Android hardware decode characteristics, and end-to-end PTS skew must be measured on the target Windows/NVIDIA host and Realme X50 Pro; they are not claimed as passed by source-level CI.
