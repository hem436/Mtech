# Android Studio Build & Test Guide

## Prerequisites Setup

### 1. Android Studio Configuration
- **Android Studio Version**: Arctic Fox or newer
- **Kotlin Plugin**: Enabled
- **Android SDK**: API 30+ (Android 11+)
- **Wear OS SDK**: Install via SDK Manager

### 2. Device Requirements
- **Samsung Galaxy Watch 4** (or compatible Samsung smartwatch)
- **Android Phone** (API 26+ / Android 8.0+)
- **Galaxy Watch App** installed on phone
- **Developer Options** enabled on both devices

## Step-by-Step Build Process

### Step 1: Import Project
1. Open Android Studio
2. **File → Open** 
3. Navigate to: `c:\Users\sun\OneDrive\Documents\GitHub\Mtech\samsung app dev\AccelerometerDataTransferApp`
4. Click **OK**
5. Wait for Gradle sync (may take 2-3 minutes)

### Step 2: Resolve Dependencies
If Gradle sync fails, check these:

#### Common Issues & Fixes:
```gradle
// In build.gradle (Project level) - already configured
buildscript {
    ext {
        compose_version = '1.5.4'
        dagger_hilt_version = '2.48'
    }
}
```

#### SDK Requirements:
- **compileSdk**: 34
- **minSdk**: 30 (wear), 26 (mobile)
- **targetSdk**: 34

### Step 3: Configure Build Variants
1. **Build → Select Build Variant**
2. For each module, select **debug**:
   - `common`: debug
   - `wear`: debug  
   - `mobile`: debug

### Step 4: Enable Developer Options

#### On Samsung Galaxy Watch 4:
1. **Settings → About watch → Software**
2. Tap **Software version** 7 times
3. **Settings → Developer options → ADB debugging** → Enable
4. **Settings → Developer options → Debug over Bluetooth** → Enable

#### On Android Phone:
1. **Settings → About phone → Software information**
2. Tap **Build number** 7 times
3. **Settings → Developer options → USB debugging** → Enable
4. **Settings → Developer options → Bluetooth debugging** → Enable

## Building the Apps

### Method 1: Using Android Studio GUI

#### Build Wear App:
1. In Project panel, select **wear** module
2. **Build → Make Module 'AccelerometerDataTransferApp.wear'**
3. Wait for build completion

#### Build Mobile App:
1. In Project panel, select **mobile** module  
2. **Build → Make Module 'AccelerometerDataTransferApp.mobile'**
3. Wait for build completion

### Method 2: Using Terminal in Android Studio
1. **View → Tool Windows → Terminal**
2. Run build commands:

```bash
# Build all modules
./gradlew build

# Build specific modules
./gradlew :common:build
./gradlew :wear:build  
./gradlew :mobile:build

# Clean and rebuild
./gradlew clean build
```

## Device Connection & Installation

### Step 1: Connect Samsung Galaxy Watch 4

#### Option A: Bluetooth Connection (Recommended)
1. Ensure watch is paired with phone via Galaxy Watch app
2. Enable **Debug over Bluetooth** on watch
3. In Android Studio: **Run → Edit Configurations → Wear**
4. Set **Target**: Choose connected device

#### Option B: WiFi Connection
1. Connect watch to same WiFi as development machine
2. **Settings → Developer options → Debug over WiFi** → Enable
3. Note the IP address shown
4. In Android Studio terminal: `adb connect [watch-ip]:5555`

### Step 2: Connect Android Phone
1. Connect phone via USB cable
2. Enable **USB debugging**
3. Accept debugging authorization popup
4. Verify connection: `adb devices`

### Step 3: Install Applications

#### Install Wear App:
1. **Run → Edit Configurations**
2. Create new **Android App** configuration
3. **Module**: wear
4. **Target**: Samsung Galaxy Watch 4
5. Click **Run** ▶️

Or use terminal:
```bash
./gradlew :wear:installDebug
```

#### Install Mobile App:
1. **Run → Edit Configurations** 
2. Create new **Android App** configuration
3. **Module**: mobile
4. **Target**: Android Phone
5. Click **Run** ▶️

Or use terminal:
```bash
./gradlew :mobile:installDebug
```

## Testing the Application

### Step 1: Grant Permissions

#### On Watch:
1. Open "Accelerometer Tracker" app
2. Grant **Body Sensors** permission when prompted
3. Allow **Wake Lock** permission

#### On Phone:
1. Open "Accelerometer Data Receiver" app  
2. Grant **Storage** permissions when prompted

### Step 2: Test Data Collection
1. **On Watch**: Tap ▶️ (Play) button to start data collection
2. **Verify**: Real-time X, Y, Z values should appear
3. **Move Watch**: Values should change as you move the watch
4. **Check Sampling**: Should collect ~100 samples per second

### Step 3: Test Data Transfer
1. **On Watch**: Tap 📤 (Send) button after collecting data
2. **Verify**: "Data sent successfully" toast should appear
3. **On Phone**: App should automatically open showing received data
4. **Check CSV**: File should be created in Documents folder

### Step 4: Verify CSV Output
1. **On Phone**: Navigate to file location:
   ```
   /Android/data/com.samsung.health.accelerometer.mobile/files/Documents/
   ```
2. **Find File**: `accelerometer_data_YYYYMMDD_HHMMSS.csv`
3. **Check Format**:
   ```csv
   timestamp,x,y,z,formatted_time
   1693123456789,0.123,-9.456,2.789,2023-08-27 15:30:56.789
   ```

## Debugging Tips

### Viewing Logs
1. **View → Tool Windows → Logcat**
2. **Filter by Tag**:
   - `AccelerometerRepositoryImpl`: Sensor data
   - `MainViewModel`: App state
   - `DataListenerService`: Data transfer
   - `CsvDataSaver`: File operations

### Common Issues

#### Build Errors:
- **Clean Project**: `Build → Clean Project`
- **Invalidate Caches**: `File → Invalidate Caches and Restart`
- **Check SDK**: Ensure Android SDK 34 is installed

#### Connection Issues:
- **Restart ADB**: `adb kill-server && adb start-server`
- **Re-pair Devices**: Disconnect and reconnect Bluetooth
- **Check Permissions**: Ensure developer options are enabled

#### Sensor Issues:
- **Check Permissions**: Body sensors permission required
- **Samsung Health**: Ensure Samsung Health SDK is properly integrated
- **Device Compatibility**: Verify Samsung Galaxy Watch 4 compatibility

#### Data Transfer Issues:
- **Check Pairing**: Ensure watch and phone are paired
- **Restart Apps**: Close and reopen both applications
- **Check Logs**: Look for Wearable API connection errors

## Performance Monitoring

### Monitor Data Collection Rate:
```kotlin
// Add to AccelerometerRepositoryImpl for debugging
Log.d(TAG, "Data rate: ${dataCount}/${timeElapsed}ms = ${dataCount*1000/timeElapsed}Hz")
```

### Monitor Memory Usage:
1. **View → Tool Windows → Profiler**
2. **Select Device** → Samsung Galaxy Watch 4
3. **Monitor**: CPU, Memory, Network usage

### File Size Monitoring:
- **100Hz for 10 seconds** = ~1000 samples = ~50KB CSV file
- **Monitor storage**: Check available space on phone

## Production Build

### For Release:
```bash
# Build release APKs
./gradlew :wear:assembleRelease
./gradlew :mobile:assembleRelease
```

### APK Locations:
- **Wear**: `wear/build/outputs/apk/release/wear-release.apk`
- **Mobile**: `mobile/build/outputs/apk/release/mobile-release.apk`

This guide covers the complete process from build to testing. The application should now be ready for use on Samsung Galaxy Watch 4!
