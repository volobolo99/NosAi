package com.playai.guardai.telemetry.storage

import com.playai.guardai.telemetry.PerceptionFrame
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class TelemetryBatchStore(private val dao: TelemetryDao) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val mutex = Mutex()
    private val pending = ArrayList<TelemetryEntity>()
    init { scope.launch { while (isActive) { delay(60_000); flush() } } }
    suspend fun enqueue(frame: PerceptionFrame) = mutex.withLock {
        pending += TelemetryEntity(frame.frameId, frame.presentationTimestampUs, frame.threatLevel, frame.disagreementDelta, frame.systemStatusFlags)
    }
    suspend fun flush() {
        val batch = mutex.withLock { if (pending.isEmpty()) return; pending.toList().also { pending.clear() } }
        dao.insertBatch(batch)
    }
    fun close() { scope.cancel() }
}
