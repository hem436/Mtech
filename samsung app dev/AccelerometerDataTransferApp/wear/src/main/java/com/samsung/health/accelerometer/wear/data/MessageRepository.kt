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
import com.google.android.gms.tasks.Task
import com.google.android.gms.wearable.MessageApi
import com.google.android.gms.wearable.MessageClient
import com.google.android.gms.wearable.Node
import com.google.android.gms.wearable.Wearable
import kotlinx.coroutines.tasks.await
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "MessageRepository"
private const val MESSAGE_PATH = "/msg"

@Singleton
class MessageRepository @Inject constructor(
    private val context: Context
) {

    private val messageClient: MessageClient by lazy {
        Wearable.getMessageClient(context)
    }

    suspend fun sendMessage(data: String): Boolean {
        return try {
            val nodes = getNodes()
            if (nodes.isNotEmpty()) {
                for (node in nodes) {
                    val result = messageClient.sendMessage(
                        node.id,
                        MESSAGE_PATH,
                        data.toByteArray()
                    ).await()
                    Log.i(TAG, "Message sent successfully to ${node.displayName}: $result")
                }
                true
            } else {
                Log.w(TAG, "No connected nodes found")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send message", e)
            false
        }
    }

    private suspend fun getNodes(): List<Node> {
        return try {
            val nodeClient = Wearable.getNodeClient(context)
            val connectedNodes = nodeClient.connectedNodes.await()
            Log.i(TAG, "Connected nodes: ${connectedNodes.size}")
            connectedNodes
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get nodes", e)
            emptyList()
        }
    }
}
