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

import com.samsung.health.accelerometer.data.AccelerometerData
import kotlinx.coroutines.flow.Flow

interface AccelerometerRepository {
    fun hasCapabilities(): Boolean
    suspend fun track(): Flow<TrackerMessage>
    fun stopTracking()
    fun getValidAccelerometerData(): ArrayList<AccelerometerData>
}

sealed class TrackerMessage {
    class DataMessage(val accelerometerData: AccelerometerData) : TrackerMessage()
    object FlushCompletedMessage : TrackerMessage()
    class TrackerErrorMessage(val trackerError: String) : TrackerMessage()
    class TrackerWarningMessage(val trackerWarning: String) : TrackerMessage()
}
