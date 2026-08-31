package com.playai.guardai.telemetry.storage

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "telemetry_frames")
data class TelemetryEntity(
    @PrimaryKey val frameId: Long,
    val presentationTimestampUs: Long,
    val threatLevel: Float,
    val disagreementDelta: Float,
    val systemStatusFlags: Int
)
