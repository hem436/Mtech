/*
 * Copyright 2023 Samsung Electronics Co., Ltd. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.samsung.health.accelerometer.mobile.data

import android.content.Context
import android.os.Environment
import android.util.Log
import com.samsung.health.accelerometer.data.AccelerometerData
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*

private const val TAG = "CsvDataSaver"

object CsvDataSaver {
    
    fun saveAccelerometerData(context: Context, jsonData: String) {
        try {
            // Parse JSON data
            val accelerometerDataList: List<AccelerometerData> = Json.decodeFromString(jsonData)
            
            // Create CSV file
            val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
            val fileName = "accelerometer_data_$timestamp.csv"
            
            // Use external storage for CSV files
            val csvFile = File(context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS), fileName)
            
            // Create directories if they don't exist
            csvFile.parentFile?.mkdirs()
            
            // Write CSV header and data
            FileWriter(csvFile, true).use { writer ->
                // Write header if file is new
                if (csvFile.length() == 0L) {
                    writer.appendLine("timestamp,x,y,z,formatted_time")
                }
                
                // Write data
                accelerometerDataList.forEach { data ->
                    val formattedTime = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault()).format(Date(data.timestamp))
                    writer.appendLine("${data.timestamp},${data.x},${data.y},${data.z},$formattedTime")
                }
            }
            
            Log.i(TAG, "Saved ${accelerometerDataList.size} data points to ${csvFile.absolutePath}")
            
        } catch (e: Exception) {
            Log.e(TAG, "Error saving accelerometer data to CSV", e)
        }
    }
}
