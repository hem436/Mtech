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

package com.samsung.health.accelerometer.wear.presentation

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.samsung.android.service.health.tracking.HealthTrackingService
import com.samsung.health.accelerometer.data.AccelerometerData
import com.samsung.health.accelerometer.wear.data.ConnectionMessage
import com.samsung.health.accelerometer.wear.data.TrackerMessage
import com.samsung.health.accelerometer.wear.domain.AreTrackingCapabilitiesAvailableUseCase
import com.samsung.health.accelerometer.wear.domain.MakeConnectionToHealthTrackingServiceUseCase
import com.samsung.health.accelerometer.wear.domain.SendMessageUseCase
import com.samsung.health.accelerometer.wear.domain.StopTrackingUseCase
import com.samsung.health.accelerometer.wear.domain.TrackAccelerometerUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val TAG = "MainViewModel"

@HiltViewModel
class MainViewModel @Inject constructor(
    private val makeConnectionToHealthTrackingServiceUseCase: MakeConnectionToHealthTrackingServiceUseCase,
    private val sendMessageUseCase: SendMessageUseCase,
    private val stopTrackingUseCase: StopTrackingUseCase,
    private val areTrackingCapabilitiesAvailableUseCase: AreTrackingCapabilitiesAvailableUseCase
) : ViewModel() {

    private val _messageSentToast = MutableSharedFlow<Boolean>()
    val messageSentToast = _messageSentToast.asSharedFlow()

    private val _trackingState = MutableStateFlow(
        TrackingState(
            trackingRunning = false,
            trackingError = false,
            currentData = AccelerometerData(),
            message = ""
        )
    )
    val trackingState: StateFlow<TrackingState> = _trackingState

    private val _connectionState = MutableStateFlow(
        ConnectionState(connected = false, message = "", null)
    )
    val connectionState: StateFlow<ConnectionState> = _connectionState

    @Inject
    lateinit var trackAccelerometerUseCase: TrackAccelerometerUseCase

    private var trackingJob: Job? = null

    fun stopTracking() {
        stopTrackingUseCase()
        trackingJob?.cancel()
        _trackingState.value = TrackingState(
            trackingRunning = false,
            trackingError = false,
            currentData = AccelerometerData(),
            message = ""
        )
    }

    fun setUpTracking() {
        Log.i(TAG, "setUpTracking()")
        viewModelScope.launch {
            makeConnectionToHealthTrackingServiceUseCase().collect { connectionMessage ->
                Log.i(TAG, "makeConnectionToHealthTrackingServiceUseCase().collect")
                when (connectionMessage) {
                    is ConnectionMessage.ConnectionSuccessMessage -> {
                        Log.i(TAG, "ConnectionMessage.ConnectionSuccessMessage")
                        _connectionState.value = ConnectionState(
                            connected = true,
                            message = "Connected to Health Tracking Service",
                            connectionException = null
                        )
                    }

                    is ConnectionMessage.ConnectionFailedMessage -> {
                        Log.i(TAG, "Connection: Something went wrong")
                        _connectionState.value = ConnectionState(
                            connected = false,
                            message = "Connection to Health Tracking Service failed",
                            connectionException = connectionMessage.exception
                        )
                    }

                    is ConnectionMessage.ConnectionEndedMessage -> {
                        Log.i(TAG, "Connection ended")
                        _connectionState.value = ConnectionState(
                            connected = false,
                            message = "Connection ended. Try again later",
                            connectionException = null
                        )
                    }
                }
            }
        }
    }

    fun sendMessage() {
        viewModelScope.launch {
            if (sendMessageUseCase()) {
                _messageSentToast.emit(true)
            } else {
                _messageSentToast.emit(false)
            }
        }
    }

    private fun processAccelerometerUpdate(accelerometerData: AccelerometerData) {
        Log.d(TAG, "Accelerometer data: x=${accelerometerData.x}, y=${accelerometerData.y}, z=${accelerometerData.z}")
        
        _trackingState.value = TrackingState(
            trackingRunning = true,
            trackingError = false,
            currentData = accelerometerData,
            message = ""
        )
    }

    fun startTracking() {
        trackingJob?.cancel()
        Log.i(TAG, "startTracking()")
        if (areTrackingCapabilitiesAvailableUseCase()) {
            trackingJob = viewModelScope.launch {
                trackAccelerometerUseCase().collect { trackerMessage ->
                    when (trackerMessage) {
                        is TrackerMessage.DataMessage -> {
                            processAccelerometerUpdate(trackerMessage.accelerometerData)
                            Log.v(TAG, "TrackerMessage.DataMessage")
                        }

                        is TrackerMessage.FlushCompletedMessage -> {
                            Log.i(TAG, "TrackerMessage.FlushCompletedMessage")
                            _trackingState.value = TrackingState(
                                trackingRunning = false,
                                trackingError = false,
                                currentData = AccelerometerData(),
                                message = ""
                            )
                        }

                        is TrackerMessage.TrackerErrorMessage -> {
                            Log.i(TAG, "TrackerMessage.TrackerErrorMessage")
                            _trackingState.value = TrackingState(
                                trackingRunning = false,
                                trackingError = true,
                                currentData = AccelerometerData(),
                                message = trackerMessage.trackerError
                            )
                        }

                        is TrackerMessage.TrackerWarningMessage -> {
                            Log.i(TAG, "TrackerMessage.TrackerWarningMessage")
                            _trackingState.value = TrackingState(
                                trackingRunning = true,
                                trackingError = false,
                                currentData = _trackingState.value.currentData,
                                message = trackerMessage.trackerWarning
                            )
                        }
                    }
                }
            }
        } else {
            _trackingState.value = TrackingState(
                trackingRunning = false,
                trackingError = true,
                currentData = AccelerometerData(),
                message = "Accelerometer tracking capabilities not available"
            )
        }
    }
}

data class ConnectionState(
    val connected: Boolean,
    val message: String,
    val connectionException: HealthTrackingService.HealthTrackingServiceException?
)

data class TrackingState(
    val trackingRunning: Boolean,
    val trackingError: Boolean,
    val currentData: AccelerometerData,
    val message: String
)
