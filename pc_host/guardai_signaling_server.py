import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SignalingServer")
app = FastAPI(title="GuardAi Signaling", docs_url=None, redoc_url=None)

REALME_ID = "REALME_X50_PRO_GUARD"

class SessionHub:
    def __init__(self):
        self.pc_ws = None
        self.realme_ws = None
        self.authenticated = False
    def reset(self):
        self.pc_ws = None
        self.realme_ws = None
        self.authenticated = False

hub = SessionHub()

@app.websocket("/ws/signaling")
async def signaling_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            packet = json.loads(await websocket.receive_text())
            m_type = packet.get("type")
            if m_type == "HEARTBEAT":
                await websocket.send_text(json.dumps({"type": "HEARTBEAT_ACK"}))
                continue
            if m_type == "CMD_PAIRING_REQUEST":
                payload = packet.get("payload", {})
                role = payload.get("role")
                if role == "PC_HOST":
                    hub.pc_ws = websocket
                    await websocket.send_text(json.dumps({"type": "PAIRING_APPROVED"}))
                elif role == "REALME_CLIENT":
                    if payload.get("device_id") != REALME_ID:
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        return
                    hub.realme_ws = websocket
                    hub.authenticated = hub.pc_ws is not None
                    await websocket.send_text(json.dumps({
                        "type": "PAIRING_APPROVED",
                        "payload": {"capability_set": ["H264_HW_DECODE", "PROTOBUF_DATACHANNELS"]}
                    }))
                    if hub.pc_ws:
                        await hub.pc_ws.send_text(json.dumps({"type": "CLIENT_CONNECTED"}))
                continue
            if m_type in {"SDP_OFFER", "SDP_ANSWER", "ICE_CANDIDATE"}:
                if not hub.authenticated:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                peer = hub.realme_ws if websocket == hub.pc_ws else hub.pc_ws
                if peer:
                    await peer.send_text(json.dumps(packet))
    except WebSocketDisconnect:
        if websocket == hub.realme_ws and hub.pc_ws:
            await hub.pc_ws.send_text(json.dumps({"type": "SIGNAL_LOST_FORCE_OFFLINE"}))
        hub.reset()
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Invalid signaling packet: %s", exc)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        hub.reset()
