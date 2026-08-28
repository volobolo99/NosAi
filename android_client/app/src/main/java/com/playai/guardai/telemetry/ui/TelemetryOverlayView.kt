package com.playai.guardai.telemetry.ui

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.*
import com.playai.guardai.telemetry.PerceptionFrame
import java.util.concurrent.ConcurrentHashMap

enum class MissionSolverMode { FAST, SMART, DEEP, LOW_RES }

open class TelemetryOverlayView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : SurfaceView(context, attrs, defStyleAttr), SurfaceHolder.Callback, Runnable {
    @Volatile protected var isRunning = false
    private var renderThread: Thread? = null
    protected val telemetryBuffer = ConcurrentHashMap<Long, PerceptionFrame>()
    @Volatile var currentVideoPTS: Long = 0L

    private val boxPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { style = Paint.Style.STROKE; strokeWidth = 5f }
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.GREEN; textSize = 36f }

    init {
        holder.addCallback(this)
        setZOrderOnTop(true)
        holder.setFormat(PixelFormat.TRANSPARENT)
    }

    fun onTelemetryPacketReceived(packet: PerceptionFrame) {
        telemetryBuffer[packet.presentationTimestampUs] = packet
        if (telemetryBuffer.size > 120) telemetryBuffer.keys.minOrNull()?.let(telemetryBuffer::remove)
    }

    fun onVideoFramePresented(ptsUs: Long) { currentVideoPTS = ptsUs }

    override fun surfaceCreated(holder: SurfaceHolder) {
        isRunning = true
        renderThread = Thread(this, "GuardAi-Overlay").also { it.start() }
    }
    override fun surfaceChanged(holder: SurfaceHolder, format: Int, w: Int, h: Int) = Unit
    override fun surfaceDestroyed(holder: SurfaceHolder) {
        isRunning = false
        renderThread?.interrupt()
        renderThread?.join(250)
        renderThread = null
    }

    override fun run() {
        while (isRunning && !Thread.currentThread().isInterrupted) {
            val canvas = try { holder.lockCanvas() } catch (_: Exception) { null }
            if (canvas != null) try {
                canvas.drawColor(Color.TRANSPARENT, PorterDuff.Mode.CLEAR)
                val frame = telemetryBuffer[currentVideoPTS]
                if (frame == null) {
                    canvas.drawText("SYNC ENGINE: WAITING FOR PTS MATCH...", 40f, 60f, textPaint)
                } else {
                    for (box in frame.detectedObjectsList) {
                        boxPaint.color = if (box.confidence > .85f) Color.RED else Color.YELLOW
                        canvas.drawRect(box.xMin * width, box.yMin * height, box.xMax * width, box.yMax * height, boxPaint)
                        canvas.drawText("${box.label} (${(box.confidence * 100).toInt()}%)", box.xMin * width, box.yMin * height - 10f, textPaint)
                    }
                    canvas.drawText("FRAME ID: ${frame.frameId}", 40f, 60f, textPaint)
                    canvas.drawText("THREAT: ${(frame.threatLevel * 100).toInt()}%", 40f, 110f, textPaint)
                    canvas.drawText("DISAGREEMENT: ${(frame.disagreementDelta * 100).toInt()}%", 40f, 160f, textPaint)
                }
            } finally { holder.unlockCanvasAndPost(canvas) }
            try { Thread.sleep(16) } catch (_: InterruptedException) { break }
        }
    }
}
