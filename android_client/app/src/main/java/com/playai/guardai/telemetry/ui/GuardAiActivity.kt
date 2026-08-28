package com.playai.guardai.telemetry.ui

import android.app.Activity
import android.os.Bundle
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.Toast
import com.playai.guardai.telemetry.PerceptionFrame
import com.playai.guardai.telemetry.network.WebRtcSignalingClient
import com.playai.guardai.telemetry.storage.GuardAiDatabase
import com.playai.guardai.telemetry.storage.TelemetryBatchStore
import org.webrtc.*

class GuardAiActivity : Activity(), TelemetryOverlayViewWithGesture.TouchInteractionListener, WebRtcSignalingClient.Callback {
    private lateinit var overlayView: TelemetryOverlayViewWithGesture
    private lateinit var videoView: SurfaceViewRenderer
    private lateinit var signaling: WebRtcSignalingClient
    private lateinit var batchStore: TelemetryBatchStore
    private var peerConnection: PeerConnection? = null
    private var factory: PeerConnectionFactory? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        val root = FrameLayout(this)
        videoView = SurfaceViewRenderer(this).apply { setZOrderOnTop(false) }
        root.addView(videoView, FrameLayout.LayoutParams(-1, -1))
        overlayView = TelemetryOverlayViewWithGesture(this).apply { setInteractionListener(this@GuardAiActivity) }
        root.addView(overlayView, FrameLayout.LayoutParams(-1, -1))
        setContentView(root)

        batchStore = TelemetryBatchStore(GuardAiDatabase.get(this).telemetryDao())
        initializeWebRtc()
        val url = intent.getStringExtra("SIGNALING_URL") ?: "wss://127.0.0.1:8888/ws/signaling"
        signaling = WebRtcSignalingClient(url, this)
        signaling.connect()
    }

    private fun initializeWebRtc() {
        PeerConnectionFactory.initialize(PeerConnectionFactory.InitializationOptions.builder(this).createInitializationOptions())
        factory = PeerConnectionFactory.builder()
            .setVideoDecoderFactory(DefaultVideoDecoderFactory(EglBase.create().eglBaseContext))
            .setVideoEncoderFactory(DefaultVideoEncoderFactory(EglBase.create().eglBaseContext, true, true))
            .createPeerConnectionFactory()
        videoView.init(EglBase.create().eglBaseContext, null)
    }

    override fun onPairingApproved(capabilities: List<String>) { runOnUiThread { Toast.makeText(this, "GuardAi paired: ${capabilities.joinToString()}", Toast.LENGTH_SHORT).show() } }
    override fun onSdpOfferReceived(sdp: String) = Unit
    override fun onIceCandidateReceived(sdpMid: String, sdpMLineIndex: Int, candidate: String) {
        peerConnection?.addIceCandidate(IceCandidate(sdpMid, sdpMLineIndex, candidate))
    }
    override fun onServerDisconnected() = runOnUiThread { Toast.makeText(this, "SIGNAL LOST — OFFLINE", Toast.LENGTH_LONG).show() }

    private fun consumeTelemetry(buffer: ByteArray) {
        runCatching { PerceptionFrame.parseFrom(buffer) }.onSuccess { frame ->
            overlayView.onTelemetryPacketReceived(frame)
            kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch { batchStore.enqueue(frame) }
        }
    }

    override fun onManualRecheckRequested(frameId: Long, label: String, xMin: Float, yMin: Float, xMax: Float, yMax: Float) {
        Toast.makeText(this, "🚨 Recheck: $label", Toast.LENGTH_SHORT).show()
        // Command transport remains on the negotiated unordered/unreliable DataChannel.
    }
    override fun onMissionModeChanged(newMode: MissionSolverMode) {
        Toast.makeText(this, "🧠 Modalità: ${newMode.name}", Toast.LENGTH_SHORT).show()
    }
    override fun onDestroy() {
        signaling.close(); peerConnection?.close(); videoView.release(); batchStore.close(); super.onDestroy()
    }
}
