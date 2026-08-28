import asyncio
import json
import logging
import time
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack

logger = logging.getLogger("WebRtcEngine")

class HardwareVideoSource:
    """Native DXGI/NVENC boundary. No CPU frame copy is permitted here."""
    async def next_encoded_or_native_frame(self):
        raise RuntimeError("DXGI/NVENC native source is not installed; fail closed")

class HardwareVideoTrack(MediaStreamTrack):
    kind = "video"
    def __init__(self, source: HardwareVideoSource):
        super().__init__()
        self.source = source
    async def recv(self):
        frame = await self.source.next_encoded_or_native_frame()
        if frame is None:
            raise RuntimeError("Hardware video source returned no frame")
        return frame

class GuardAiWebRtcEngine:
    def __init__(self, signaling_url, video_source=None):
        self.url = signaling_url
        self.pc = RTCPeerConnection()
        self.channel = None
        self.video_source = video_source or HardwareVideoSource()

    async def run(self):
        async with websockets.connect(self.url, max_size=2**20) as ws:
            await ws.send(json.dumps({"type":"CMD_PAIRING_REQUEST","payload":{"role":"PC_HOST"}}))
            approved = json.loads(await ws.recv())
            if approved.get("type") != "PAIRING_APPROVED":
                raise RuntimeError("GuardAi pairing was not approved")
            self.channel = self.pc.createDataChannel(
                "guardai_telemetry_udp", ordered=False, maxRetransmits=0
            )
            @self.channel.on("open")
            def on_open():
                asyncio.create_task(self.protobuf_loop())
            self.pc.addTrack(HardwareVideoTrack(self.video_source))
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            await ws.send(json.dumps({"type":"SDP_OFFER","payload":{"sdp":self.pc.localDescription.sdp}}))
            async for raw in ws:
                packet = json.loads(raw)
                if packet.get("type") == "SDP_ANSWER":
                    await self.pc.setRemoteDescription(RTCSessionDescription(
                        sdp=packet["payload"]["sdp"], type="answer"))
                    break
                if packet.get("type") == "ICE_CANDIDATE":
                    # Candidate handling belongs to the concrete aiortc ICE adapter.
                    continue
            await asyncio.Event().wait()

    async def protobuf_loop(self):
        """Send generated PerceptionFrame bytes, keyed by the exact video PTS."""
        try:
            from guardai_telemetry_pb2 import PerceptionFrame
        except ImportError as exc:
            raise RuntimeError("Generated telemetry protobuf module is required") from exc
        frame_id = 0
        while self.channel and self.channel.readyState == "open":
            frame_id += 1
            pts_us = time.monotonic_ns() // 1000
            packet = PerceptionFrame(frame_id=frame_id, presentation_timestamp_us=pts_us)
            self.channel.send(packet.SerializeToString())
            await asyncio.sleep(1 / 60)
