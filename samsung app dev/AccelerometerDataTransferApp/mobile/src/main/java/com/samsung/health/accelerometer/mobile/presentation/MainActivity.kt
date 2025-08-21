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

package com.samsung.health.accelerometer.mobile.presentation

import android.Manifest
import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import com.samsung.health.accelerometer.data.AccelerometerData
import com.samsung.health.accelerometer.mobile.ui.theme.AccelerometerDataTransferTheme
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import java.text.SimpleDateFormat
import java.util.*

private const val TAG = "MainActivity"

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { 
            AccelerometerDataTransferTheme {
                TheApp(intent) 
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setContent { 
            AccelerometerDataTransferTheme {
                TheApp(intent) 
            }
        }
    }

    override fun onResume() {
        super.onResume()
        Log.i(TAG, "onResume()")
    }
}

@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun TheApp(intent: Intent?) {
    val permissionsState = rememberMultiplePermissionsState(
        listOf(
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE
        )
    )

    LaunchedEffect(Unit) {
        permissionsState.launchMultiplePermissionRequest()
    }

    if (permissionsState.allPermissionsGranted) {
        val message = intent?.getStringExtra("message")
        if (message != null) {
            try {
                val accelerometerDataList: List<AccelerometerData> = Json.decodeFromString(message)
                MainScreen(accelerometerDataList)
            } catch (e: Exception) {
                Log.e(TAG, "Error parsing accelerometer data", e)
                ErrorScreen("Error parsing accelerometer data: ${e.message}")
            }
        } else {
            WelcomeScreen()
        }
    } else {
        PermissionScreen(permissionsState.shouldShowRationale)
    }
}

@Composable
fun MainScreen(accelerometerDataList: List<AccelerometerData>) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Accelerometer Data Received",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        Text(
            text = "Total samples: ${accelerometerDataList.size}",
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        
        if (accelerometerDataList.isNotEmpty()) {
            Text(
                text = "Data saved to CSV file in Documents folder",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(bottom = 16.dp)
            )
        }

        LazyColumn {
            items(accelerometerDataList.take(20)) { data -> // Show only first 20 items
                AccelerometerDataItem(data)
                Spacer(modifier = Modifier.height(8.dp))
            }
            
            if (accelerometerDataList.size > 20) {
                item {
                    Text(
                        text = "... and ${accelerometerDataList.size - 20} more samples",
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun AccelerometerDataItem(data: AccelerometerData) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            val formattedTime = SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault()).format(Date(data.timestamp))
            
            Text(
                text = "Time: $formattedTime",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(text = "X: ${String.format("%.3f", data.x)} m/s²")
            Text(text = "Y: ${String.format("%.3f", data.y)} m/s²")
            Text(text = "Z: ${String.format("%.3f", data.z)} m/s²")
        }
    }
}

@Composable
fun WelcomeScreen() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Accelerometer Data Receiver",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Waiting for data from smartwatch...",
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

@Composable
fun ErrorScreen(errorMessage: String) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Error",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.error,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = errorMessage,
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

@Composable
fun PermissionScreen(shouldShowRationale: Boolean) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Storage Permission Required",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = if (shouldShowRationale) {
                    "The app needs storage permission to save accelerometer data to CSV files."
                } else {
                    "Please grant storage permission to continue."
                },
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}
