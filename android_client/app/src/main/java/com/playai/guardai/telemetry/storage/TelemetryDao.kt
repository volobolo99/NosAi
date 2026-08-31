package com.playai.guardai.telemetry.storage

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy

@Dao
interface TelemetryDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBatch(frames: List<TelemetryEntity>)
}
