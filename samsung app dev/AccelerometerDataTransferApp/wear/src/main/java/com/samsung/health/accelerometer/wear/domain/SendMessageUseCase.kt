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

package com.samsung.health.accelerometer.wear.domain

import com.samsung.health.accelerometer.wear.data.AccelerometerRepository
import com.samsung.health.accelerometer.wear.data.MessageRepository
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject

class SendMessageUseCase @Inject constructor(
    private val messageRepository: MessageRepository,
    private val accelerometerRepository: AccelerometerRepository
) {
    suspend operator fun invoke(): Boolean {
        val data = accelerometerRepository.getValidAccelerometerData()
        return if (data.isNotEmpty()) {
            val jsonData = Json.encodeToString(data)
            messageRepository.sendMessage(jsonData)
        } else {
            false
        }
    }
}
