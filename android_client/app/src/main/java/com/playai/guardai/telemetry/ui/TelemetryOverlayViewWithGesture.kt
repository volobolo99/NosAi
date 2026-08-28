package com.playai.guardai.telemetry.ui

import android.content.Context
import android.util.AttributeSet
import android.view.GestureDetector
import android.view.HapticFeedbackConstants
import android.view.MotionEvent

class TelemetryOverlayViewWithGesture @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : TelemetryOverlayView(context, attrs, defStyleAttr) {
    interface TouchInteractionListener {
        fun onManualRecheckRequested(frameId: Long, label: String, xMin: Float, yMin: Float, xMax: Float, yMax: Float)
        fun onMissionModeChanged(newMode: MissionSolverMode)
    }
    private var listener: TouchInteractionListener? = null
    private var currentMode = MissionSolverMode.SMART
    private val detector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent) = true
        override fun onFling(e1: MotionEvent?, e2: MotionEvent?, velX: Float, velY: Float): Boolean {
            if (e1 == null || e2 == null) return false
            val dx = e2.x - e1.x; val dy = e2.y - e1.y
            if (kotlin.math.abs(dx) > kotlin.math.abs(dy) && kotlin.math.abs(dx) > 100 && kotlin.math.abs(velX) > 100) {
                shiftMode(dx > 0); return true
            }
            return false
        }
    })
    fun setInteractionListener(value: TouchInteractionListener) { listener = value }
    override fun onTouchEvent(event: MotionEvent): Boolean {
        detector.onTouchEvent(event)
        if (event.action == MotionEvent.ACTION_UP) {
            telemetryBuffer[currentVideoPTS]?.let { frame ->
                frame.detectedObjectsList.firstOrNull { box ->
                    event.x in (box.xMin * width)..(box.xMax * width) && event.y in (box.yMin * height)..(box.yMax * height)
                }?.let { box ->
                    performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY)
                    listener?.onManualRecheckRequested(frame.frameId, box.label, box.xMin, box.yMin, box.xMax, box.yMax)
                }
            }
        }
        return true
    }
    private fun shiftMode(forward: Boolean) {
        val modes = MissionSolverMode.values()
        currentMode = modes[(currentMode.ordinal + if (forward) 1 else -1 + modes.size) % modes.size]
        performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
        listener?.onMissionModeChanged(currentMode)
    }
}
