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

package com.samsung.health.accelerometer.wear.presentation.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Stop
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.wear.compose.material.*
import com.samsung.health.accelerometer.data.AccelerometerData
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun MainScreen(
    connected: Boolean,
    connectionMessage: String,
    trackingRunning: Boolean,
    trackingError: Boolean,
    errorMessage: String,
    currentData: AccelerometerData,
    onStartTracking: () -> Unit,
    onStopTracking: () -> Unit,
    onSendMessage: () -> Unit
) {
    val listState = rememberScalingLazyListState()
    val scrollState = rememberScrollState()

    Scaffold(
        timeText = {
            if (!listState.isScrollInProgress) {
                TimeText()
            }
        },
        vignette = {
            Vignette(vignettePosition = VignettePosition.TopAndBottom)
        },
        positionIndicator = {
            PositionIndicator(
                scalingLazyListState = listState
            )
        }
    ) {
        ScalingLazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(
                top = 10.dp,
                start = 10.dp,
                end = 10.dp,
                bottom = 40.dp
            ),
            verticalArrangement = Arrangement.Center,
            state = listState
        ) {
            item {
                Text(
                    modifier = Modifier.fillMaxWidth(),
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colors.primary,
                    text = "Accelerometer Tracker"
                )
            }

            item {
                Spacer(modifier = Modifier.height(8.dp))
            }

            // Connection Status
            item {
                Text(
                    modifier = Modifier.fillMaxWidth(),
                    textAlign = TextAlign.Center,
                    color = if (connected) Color.Green else Color.Red,
                    text = if (connected) "Connected" else "Disconnected"
                )
            }

            item {
                Text(
                    modifier = Modifier.fillMaxWidth(),
                    textAlign = TextAlign.Center,
                    text = connectionMessage
                )
            }

            item {
                Spacer(modifier = Modifier.height(8.dp))
            }

            // Tracking Controls
            if (connected) {
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        if (!trackingRunning) {
                            Button(
                                onClick = onStartTracking,
                                modifier = Modifier.size(60.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.PlayArrow,
                                    contentDescription = "Start"
                                )
                            }
                        } else {
                            Button(
                                onClick = onStopTracking,
                                colors = ButtonDefaults.buttonColors(backgroundColor = Color.Red),
                                modifier = Modifier.size(60.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Stop,
                                    contentDescription = "Stop"
                                )
                            }
                        }

                        Button(
                            onClick = onSendMessage,
                            modifier = Modifier.size(60.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Send,
                                contentDescription = "Send"
                            )
                        }
                    }
                }

                item {
                    Spacer(modifier = Modifier.height(8.dp))
                }

                // Current Data Display
                if (trackingRunning && !trackingError) {
                    item {
                        Card(
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(
                                modifier = Modifier.padding(8.dp)
                            ) {
                                Text(
                                    text = "Current Data:",
                                    style = MaterialTheme.typography.caption1,
                                    color = MaterialTheme.colors.primary
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = "X: ${String.format("%.3f", currentData.x)} m/s²",
                                    style = MaterialTheme.typography.body2
                                )
                                Text(
                                    text = "Y: ${String.format("%.3f", currentData.y)} m/s²",
                                    style = MaterialTheme.typography.body2
                                )
                                Text(
                                    text = "Z: ${String.format("%.3f", currentData.z)} m/s²",
                                    style = MaterialTheme.typography.body2
                                )
                                if (currentData.timestamp > 0) {
                                    val date = Date(currentData.timestamp)
                                    val formatter = SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault())
                                    Text(
                                        text = "Time: ${formatter.format(date)}",
                                        style = MaterialTheme.typography.body2
                                    )
                                }
                            }
                        }
                    }
                }

                // Error Message
                if (trackingError) {
                    item {
                        Text(
                            modifier = Modifier.fillMaxWidth(),
                            textAlign = TextAlign.Center,
                            color = Color.Red,
                            text = errorMessage
                        )
                    }
                }

                // Warning Message
                if (trackingRunning && errorMessage.isNotEmpty() && !trackingError) {
                    item {
                        Text(
                            modifier = Modifier.fillMaxWidth(),
                            textAlign = TextAlign.Center,
                            color = Color.Yellow,
                            text = errorMessage
                        )
                    }
                }
            }
        }
    }
}
