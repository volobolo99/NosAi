package com.playai.guardai.telemetry.storage

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [TelemetryEntity::class], version = 1, exportSchema = false)
abstract class GuardAiDatabase : RoomDatabase() {
    abstract fun telemetryDao(): TelemetryDao
    companion object {
        @Volatile private var instance: GuardAiDatabase? = null
        fun get(context: Context): GuardAiDatabase = instance ?: synchronized(this) {
            instance ?: Room.databaseBuilder(context.applicationContext, GuardAiDatabase::class.java, "guardai.db")
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING)
                .build().also { instance = it }
        }
    }
}
