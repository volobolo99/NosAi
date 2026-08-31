package com.playai.guardai.telemetry.ui

import android.app.Activity
import android.os.Bundle
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.Toast
import com.playai.guardai.control.ControlCommand
import com.playai.guardai.control.ManualRecheck
import com.playai.guardai.control.MissionModeChange
import com.playai.guardai.control.MissionSolverMode as ControlMissionSolverMode
import com.playai.guardai.telemetry.PerceptionFrame
import com.playai.guardai.telemetry.network.WebRtcSignalingClient
import com.playai.guardai.telemetry.storage.GuardAiDatabase
import com.playai.guardai.telemetry.storage.TelemetryBatchStore
import org.webrtc.*
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

class GuardAiActivity : Activity(), TelemetryOverlayViewWithGesture.TouchInteractionListener, WebRtcSignalingClient.Callback {
    private lateinit var overlayView: TelemetryOverlayViewWithGesture
    private lateinit var videoView: SurfaceViewRenderer
    private lateinit var signaling: WebRtcSignalingClient
    private lateinit var batchStore: TelemetryBatchStore
    private lateinit var eglBase: EglBase
    private var peerConnection: PeerConnection? = null
    private var telemetryChannel: DataChannel? = null
    private var controlChannel: DataChannel? = null
    private var factory: PeerConnectionFactory? = null
    private val ioScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val commandId = AtomicLong(0L)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        eglBase = EglBase.create()
        val root = FrameLayout(this)
        videoView = SurfaceViewRenderer(this).apply {
            setZOrderOnTop(false)
            init(eglBase.eglBaseContext, null)
        }
        root.addView(videoView, FrameLayout.LayoutParams(-1, -1))
        overlayView = TelemetryOverlayViewWithGesture(this).apply {
            setInteractionListener(this@GuardAiActivity)
        }
        root.addView(overlayView, FrameLayout.LayoutParams(-1, -1))
        setContentView(root)
        batchStore = TelemetryBatchStore(GuardAiDatabase.get(this).telemetryDao())
        initializeWebRtc()
        val url = intent.getStringExtra("SIGNALING_URL")
        if (url.isNullOrBlank()) {
            Toast.makeText(this, "GuardAi offline: SIGNALING_URL not configured", Toast.LENGTH_LONG).show()
            return
        }
        signaling = WebRtcSignalingClient(url, this)
        signaling.connect()
    }

    private fun initializeWebRtc() {
        PeerConnectionFactory.initialize(
            PeerConnectionFactory.InitializationOptions.builder(this).createInitializationOptions()
        )
        factory = PeerConnectionFactory.builder()
            .setVideoDecoderFactory(DefaultVideoDecoderFactory(eglBase.eglBaseContext))
            .setVideoEncoderFactory(DefaultVideoEncoderFactory(eglBase.eglBaseContext, true, true))
            .createPeerConnectionFactory()
    }

    override fun onPairingApproved(capabilities: List<String>) = Unit

    override fun onSdpOfferReceived(sdp: String) {
        peerConnection = factory?.createPeerConnection(emptyList(), object : PeerConnection.Observer {
            override fun onIceCandidate(candidate: IceCandidate) =
                signaling.sendIceCandidate(candidate.sdpMid ?: "", candidate.sdpMLineIndex, candidate.sdp)

            override fun onDataChannel(channel: DataChannel) {
                when (channel.label()) {
                    "guardai-control" -> attachControlChannel(channel)
                    else -> attachTelemetryChannel(channel)
                }
            }

            override fun onAddTrack(receiver: RtpReceiver, mediaStreams: Array<MediaStream>) {
                (receiver.track() as? VideoTrack)?.addSink(object : VideoSink {
                    override fun onFrame(frame: VideoFrame) {
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
            override fun onSetSuccess() {
                peerConnection?.createAnswer(answerObserver(), MediaConstraints())
            }
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

    override fun onIceCandidateReceived(sdpMid: String, sdpMLineIndex: Int, candidate: String) {
        peerConnection?.addIceCandidate(IceCandidate(sdpMid, sdpMLineIndex, candidate))
    }

    override fun onServerDisconnected() = runOnUiThread {
        Toast.makeText(this, "SIGNAL LOST — OFFLINE", Toast.LENGTH_LONG).show()
    }

    private fun attachTelemetryChannel(channel: DataChannel) {
        telemetryChannel = channel
        channel.registerObserver(object : DataChannel.Observer {
            override fun onBufferedAmountChange(previousAmount: Long) = Unit
            override fun onStateChange() = Unit
            override fun onMessage(buffer: DataChannel.Buffer) {
                if (!buffer.binary) return
                val bytes = ByteArray(buffer.data.remaining()).also { buffer.data.get(it) }
                runCatching { PerceptionFrame.parseFrom(bytes) }.onSuccess { frame ->
                    overlayView.onTelemetryPacketReceived(frame)
                    ioScope.launch { batchStore.enqueue(frame) }
                }
            }
        })
    }

    private fun attachControlChannel(channel: DataChannel) {
        controlChannel = channel
        channel.registerObserver(object : DataChannel.Observer {
            override fun onBufferedAmountChange(previousAmount: Long) = Unit
            override fun onStateChange() = Unit
            override fun onMessage(buffer: DataChannel.Buffer) = Unit
        })
    }

    private fun sendCommand(command: ControlCommand): Boolean {
        val channel = controlChannel ?: return false
        if (channel.state() != DataChannel.State.OPEN) return false
        return channel.send(DataChannel.Buffer(ByteBuffer.wrap(command.toByteArray()), true))
    }

    override fun onManualRecheckRequested(frameId: Long, label: String, xMin: Float, yMin: Float, xMax: Float, yMax: Float) {
        sendCommand(
            ControlCommand.newBuilder()
                .setCommandId(commandId.incrementAndGet())
                .setManualRecheck(
                    ManualRecheck.newBuilder()
                        .setFrameId(frameId)
                        .setLabel(label)
                        .setXMin(xMin)
                        .setYMin(yMin)
                        .setXMax(xMax)
                        .setYMax(yMax)
                        .build()
                )
                .build()
        )
    }

    override fun onMissionModeChanged(newMode: MissionSolverMode) {
        val mode = when (newMode) {
            MissionSolverMode.FAST -> ControlMissionSolverMode.FAST
            MissionSolverMode.SMART -> ControlMissionSolverMode.SMART
            MissionSolverMode.DEEP -> ControlMissionSolverMode.DEEP
            MissionSolverMode.LOW_RES -> ControlMissionSolverMode.LOW_RES
        }
        sendCommand(
            ControlCommand.newBuilder()
                .setCommandId(commandId.incrementAndGet())
                .setMissionModeChange(MissionModeChange.newBuilder().setMode(mode).build())
                .build()
        )
    }

    override fun onDestroy() {
        if (::signaling.isInitialized) signaling.close()
        telemetryChannel?.dispose()
        controlChannel?.dispose()
        peerConnection?.close()
        videoView.release()
        eglBase.release()
        batchStore.close()
        ioScope.cancel()
        factory?.dispose()
        super.onDestroy()
    }
}
