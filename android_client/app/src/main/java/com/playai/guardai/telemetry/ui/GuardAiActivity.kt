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
    private lateinit var eglBase: EglBase
    private var peerConnection: PeerConnection? = null
    private var dataChannel: DataChannel? = null
    private var factory: PeerConnectionFactory? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        eglBase = EglBase.create()
        val root = FrameLayout(this)
        videoView = SurfaceViewRenderer(this).apply { setZOrderOnTop(false); init(eglBase.eglBaseContext, null) }
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
            .setVideoDecoderFactory(DefaultVideoDecoderFactory(eglBase.eglBaseContext))
            .setVideoEncoderFactory(DefaultVideoEncoderFactory(eglBase.eglBaseContext, true, true))
            .createPeerConnectionFactory()
    }

    override fun onPairingApproved(capabilities: List<String>) = Unit
    override fun onSdpOfferReceived(sdp: String) {
        peerConnection = factory?.createPeerConnection(emptyList(), object : PeerConnection.Observer {
            override fun onIceCandidate(candidate: IceCandidate) = signaling.sendIceCandidate(candidate.sdpMid ?: "", candidate.sdpMLineIndex, candidate.sdp)
            override fun onDataChannel(channel: DataChannel) = attachDataChannel(channel)
            override fun onAddTrack(receiver: RtpReceiver, mediaStreams: Array<MediaStream>) {
                (receiver.track() as? VideoTrack)?.addSink(object : VideoSink {
                    override fun onFrame(frame: VideoFrame) {
                        // The sender-side PTS is expected to survive the negotiated WebRTC media path.
                        overlayView.onVideoFramePresented(frame.timestampNs / 1000L)
                        videoView.onFrame(frame)
                    }
                })
            }
            override fun onSignalingChange(state: PeerConnection.SignalingState) = Unit
            override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) = Unit
            override fun onIceConnectionReceivingChange(receiving: Boolean) = Unit
            override fun onIceGatheringChange(state: PeerConnection.IceGatheringState) = Unit
            override fun onIceCandidatesRemoved(candidates: Array<IceCandidate>) = Unit
            override fun onRemoveStream(stream: MediaStream) = Unit
            override fun onRenegotiationNeeded() = Unit
            override fun onConnectionChange(newState: PeerConnection.PeerConnectionState) = Unit
        })
        peerConnection?.setRemoteDescription(object : SdpObserver {
            override fun onSetSuccess() { peerConnection?.createAnswer(answerObserver(), MediaConstraints()) }
            override fun onCreateSuccess(d: SessionDescription) = Unit
            override fun onCreateFailure(e: String) = Unit
            override fun onSetFailure(e: String) = Unit
        }, SessionDescription(SessionDescription.Type.OFFER, sdp))
    }

    private fun answerObserver() = object : SdpObserver {
        override fun onCreateSuccess(answer: SessionDescription) {
            peerConnection?.setLocalDescription(object : SdpObserver {
                override fun onSetSuccess() = signaling.sendSdpAnswer(answer.description)
                override fun onCreateSuccess(d: SessionDescription) = Unit
                override fun onCreateFailure(e: String) = Unit
                override fun onSetFailure(e: String) = Unit
            }, answer)
        }
        override fun onSetSuccess() = Unit
        override fun onCreateFailure(e: String) = Unit
        override fun onSetFailure(e: String) = Unit
    }

    override fun onIceCandidateReceived(sdpMid: String, sdpMLineIndex: Int, candidate: String) { peerConnection?.addIceCandidate(IceCandidate(sdpMid, sdpMLineIndex, candidate)) }
    override fun onServerDisconnected() = runOnUiThread { Toast.makeText(this, "SIGNAL LOST — OFFLINE", Toast.LENGTH_LONG).show() }

    private fun attachDataChannel(channel: DataChannel) {
        dataChannel = channel
        channel.registerObserver(object : DataChannel.Observer {
            override fun onBufferedAmountChange(previousAmount: Long) = Unit
            override fun onStateChange() = Unit
            override fun onMessage(buffer: DataChannel.Buffer) {
                if (!buffer.binary) return
                val bytes = ByteArray(buffer.data.remaining()).also { buffer.data.get(it) }
                runCatching { PerceptionFrame.parseFrom(bytes) }.onSuccess { frame ->
                    overlayView.onTelemetryPacketReceived(frame)
                    kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch { batchStore.enqueue(frame) }
                }
            }
        })
    }

    private fun sendCommand(type: String, payload: Map<String, Any?>) { /* command protobuf adapter boundary */ }
    override fun onManualRecheckRequested(frameId: Long, label: String, xMin: Float, yMin: Float, xMax: Float, yMax: Float) = sendCommand("CMD_RECHECK", mapOf("frame_id" to frameId, "label" to label, "x_min" to xMin, "y_min" to yMin, "x_max" to xMax, "y_max" to yMax))
    override fun onMissionModeChanged(newMode: MissionSolverMode) = sendCommand("CMD_MODE_SWITCH", mapOf("mode" to newMode.name))
    override fun onDestroy() { signaling.close(); dataChannel?.dispose(); peerConnection?.close(); videoView.release(); eglBase.release(); batchStore.close(); factory?.dispose(); super.onDestroy() }
}
