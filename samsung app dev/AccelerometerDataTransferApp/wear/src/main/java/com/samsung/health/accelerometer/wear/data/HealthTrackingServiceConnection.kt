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
import com.samsung.android.service.health.tracking.HealthTrackingService
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class HealthTrackingServiceConnection @Inject constructor(
    @ApplicationContext private val context: Context,
    private val coroutineScope: CoroutineScope,
) {

    private val _connectionFlow = MutableSharedFlow<ConnectionMessage>()
    val connectionFlow: SharedFlow<ConnectionMessage> = _connectionFlow.asSharedFlow()

    private var healthTrackingService: HealthTrackingService? = null

    private val connectionListener = object : HealthTrackingService.ConnectionListener {

        override fun onConnectionSuccess() {
            coroutineScope.launch {
                _connectionFlow.emit(ConnectionMessage.ConnectionSuccessMessage)
            }
        }

        override fun onConnectionEnded() {
            coroutineScope.launch {
                _connectionFlow.emit(ConnectionMessage.ConnectionEndedMessage)
            }
        }

        override fun onConnectionFailed(exception: HealthTrackingService.HealthTrackingServiceException) {
            coroutineScope.launch {
                _connectionFlow.emit(ConnectionMessage.ConnectionFailedMessage(exception))
            }
        }
    }

    fun connect() {
        healthTrackingService = HealthTrackingService(connectionListener, context)
        healthTrackingService?.connectService()
    }

    fun getHealthTrackingService(): HealthTrackingService? {
        return healthTrackingService
    }
}

sealed class ConnectionMessage {
    object ConnectionSuccessMessage : ConnectionMessage()
    object ConnectionEndedMessage : ConnectionMessage()
    class ConnectionFailedMessage(val exception: HealthTrackingService.HealthTrackingServiceException) : ConnectionMessage()
}
