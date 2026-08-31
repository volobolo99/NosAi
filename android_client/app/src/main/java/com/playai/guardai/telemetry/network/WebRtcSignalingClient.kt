package com.playai.guardai.telemetry.network

import android.util.Log
import okhttp3.*
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class WebRtcSignalingClient(private val serverUrl: String, private val callback: Callback) : WebSocketListener() {
    interface Callback {
        fun onPairingApproved(capabilities: List<String>)
        fun onSdpOfferReceived(sdp: String)
        fun onIceCandidateReceived(sdpMid: String, sdpMLineIndex: Int, candidate: String)
        fun onServerDisconnected()
    }
    private val client = OkHttpClient.Builder().readTimeout(0, TimeUnit.MILLISECONDS).build()
    private var ws: WebSocket? = null
    fun connect() { ws = client.newWebSocket(Request.Builder().url(serverUrl).build(), this) }
    override fun onOpen(webSocket: WebSocket, response: Response) {
        webSocket.send(JSONObject().apply {
            put("type", "CMD_PAIRING_REQUEST")
            put("payload", JSONObject().apply { put("device_id", "REALME_X50_PRO_GUARD"); put("role", "REALME_CLIENT") })
        }.toString())
    }
    override fun onMessage(webSocket: WebSocket, text: String) {
        runCatching {
            val packet = JSONObject(text)
            when (packet.getString("type")) {
                "PAIRING_APPROVED" -> {
                    val arr = packet.optJSONObject("payload")?.optJSONArray("capability_set")
                    callback.onPairingApproved((0 until (arr?.length() ?: 0)).map { arr!!.getString(it) })
                }
                "SDP_OFFER" -> callback.onSdpOfferReceived(packet.getJSONObject("payload").getString("sdp"))
                "ICE_CANDIDATE" -> packet.getJSONObject("payload").let { callback.onIceCandidateReceived(it.getString("sdpMid"), it.getInt("sdpMLineIndex"), it.getString("candidate")) }
            }
        }.onFailure { Log.w("GuardAiSignal", "Invalid signaling packet", it) }
    }
    fun sendSdpAnswer(sdp: String) = send("SDP_ANSWER", JSONObject().put("sdp", sdp))
    fun sendIceCandidate(sdpMid: String, sdpMLineIndex: Int, candidate: String) = send("ICE_CANDIDATE", JSONObject().apply { put("sdpMid", sdpMid); put("sdpMLineIndex", sdpMLineIndex); put("candidate", candidate) })
    private fun send(type: String, payload: JSONObject) { ws?.send(JSONObject().put("type", type).put("payload", payload).toString()) }
    fun close() { ws?.close(1000, "GuardAi shutdown"); ws = null }
    override fun onClosing(webSocket: WebSocket, code: Int, reason: String) { callback.onServerDisconnected() }
    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) { callback.onServerDisconnected() }
}
