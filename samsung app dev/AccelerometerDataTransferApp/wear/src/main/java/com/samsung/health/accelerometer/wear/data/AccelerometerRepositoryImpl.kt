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

package com.samsung.health.accelerometer.wear.data

import android.content.Context
import android.util.Log
import com.samsung.android.service.health.tracking.HealthTracker
import com.samsung.android.service.health.tracking.HealthTrackingService
import com.samsung.android.service.health.tracking.data.DataPoint
import com.samsung.android.service.health.tracking.data.HealthTrackerType
import com.samsung.android.service.health.tracking.data.ValueKey
import com.samsung.health.accelerometer.data.AccelerometerData
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.channels.trySendBlocking
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "AccelerometerRepositoryImpl"

@OptIn(ExperimentalCoroutinesApi::class)
@Singleton
class AccelerometerRepositoryImpl @Inject constructor(
    private val coroutineScope: CoroutineScope,
    private val healthTrackingServiceConnection: HealthTrackingServiceConnection,
    @ApplicationContext private val context: Context,
) : AccelerometerRepository {

    private val trackingType = HealthTrackerType.ACCELEROMETER
    private var listenerSet = false
    private var healthTrackingService: HealthTrackingService? = null

    private val maxValuesToKeep = 1000 // Keep more data for 100Hz sampling
    private var accelerometerTracker: HealthTracker? = null
    private var validAccelerometerData = ArrayList<AccelerometerData>()

    override fun getValidAccelerometerData(): ArrayList<AccelerometerData> {
        return validAccelerometerData
    }

    private fun trimDataList() {
        val howManyElementsToRemove = validAccelerometerData.size - maxValuesToKeep
        repeat(howManyElementsToRemove) { validAccelerometerData.removeFirstOrNull() }
    }

    @ExperimentalCoroutinesApi
    override suspend fun track(): Flow<TrackerMessage> = callbackFlow {
        val updateListener = object : HealthTracker.TrackerEventListener {
            override fun onDataReceived(dataPoints: MutableList<DataPoint>) {
                for (dataPoint in dataPoints) {
                    val timestamp = dataPoint.timestamp
                    
                    // Get accelerometer values
                    val xValue = dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_X)
                    val yValue = dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Y)
                    val zValue = dataPoint.getValue(ValueKey.AccelerometerSet.ACCELEROMETER_Z)

                    val accelerometerData = AccelerometerData(
                        timestamp = timestamp,
                        x = xValue,
                        y = yValue,
                        z = zValue
                    )

                    Log.d(TAG, "Accelerometer data: timestamp=$timestamp, x=$xValue, y=$yValue, z=$zValue")

                    validAccelerometerData.add(accelerometerData)

                    coroutineScope.runCatching {
                        trySendBlocking(TrackerMessage.DataMessage(accelerometerData))
                    }
                }
                trimDataList()
            }

            override fun onFlushCompleted() {
                Log.i(TAG, "onFlushCompleted()")
                coroutineScope.runCatching {
                    trySendBlocking(TrackerMessage.FlushCompletedMessage)
                }
            }

            override fun onError(trackerError: HealthTracker.TrackerError?) {
                Log.e(TAG, "onError(): $trackerError")
                coroutineScope.runCatching {
                    trySendBlocking(TrackerMessage.TrackerErrorMessage(trackerError.toString()))
                }
            }
        }

        accelerometerTracker = healthTrackingService!!.getHealthTracker(trackingType)
        
        // Set sampling rate to 100Hz
        accelerometerTracker?.let { tracker ->
            val config = hashMapOf<String, Any>()
            config["SamplingRate"] = 100 // 100Hz sampling rate
            tracker.setConfig(config)
        }

        setListener(updateListener)

        awaitClose {
            Log.i(TAG, "Tracking flow awaitClose()")
            stopTracking()
        }
    }

    override fun stopTracking() {
        unsetListener()
    }

    private fun unsetListener() {
        if (listenerSet) {
            accelerometerTracker?.unsetEventListener()
            listenerSet = false
        }
    }

    private fun setListener(listener: HealthTracker.TrackerEventListener) {
        if (!listenerSet) {
            accelerometerTracker?.setEventListener(listener)
            listenerSet = true
        }
    }

    override fun hasCapabilities(): Boolean {
        Log.i(TAG, "hasCapabilities()")
        healthTrackingService = healthTrackingServiceConnection.getHealthTrackingService()
        val trackers: List<HealthTrackerType> =
            healthTrackingService!!.trackingCapability.supportHealthTrackerTypes
        return trackers.contains(trackingType)
    }
}
