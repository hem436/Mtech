# Android Studio Build & Run Instructions

## Quick Start

### 1. Prerequisites
- **Android Studio** (Arctic Fox or newer)
- **Java 11+** (for Gradle builds)
- **Samsung Galaxy Watch 4** 
- **Android Phone** with Galaxy Watch app

### 2. Open Project in Android Studio
1. Launch Android Studio
2. **File → Open**
3. Navigate to: `c:\Users\sun\OneDrive\Documents\GitHub\Mtech\samsung app dev\AccelerometerDataTransferApp`
4. Click **OK**
5. **Wait for Gradle sync** (may take 2-3 minutes)

### 3. Enable Developer Options

**Samsung Galaxy Watch 4:**
```
Settings → About watch → Software → Tap "Software version" 7 times
Settings → Developer options → ADB debugging → Enable
Settings → Developer options → Debug over Bluetooth → Enable
```

**Android Phone:**
```
Settings → About phone → Tap "Build number" 7 times  
Settings → Developer options → USB debugging → Enable
```

### 4. Build the Project

**Option A: Android Studio GUI**
1. **Build → Clean Project**
2. **Build → Rebuild Project** 
3. Check for any errors in Build Output

**Option B: Terminal (if Java is configured)**
```bash
gradlew clean build
```

### 5. Install Apps

**Install on Samsung Galaxy Watch 4:**
1. **Run → Edit Configurations**
2. **+ → Android App**
3. **Name**: Wear App
4. **Module**: wear
5. **Target Device**: Samsung Galaxy Watch 4
6. Click **Run ▶️**

**Install on Android Phone:**
1. **Run → Edit Configurations**
2. **+ → Android App** 
3. **Name**: Mobile App
4. **Module**: mobile
5. **Target Device**: Android Phone
6. Click **Run ▶️**

## Testing the Application

### 1. Grant Permissions
- **Watch**: Allow Body Sensors permission
- **Phone**: Allow Storage permissions

### 2. Test Data Flow
1. **On Watch**: Open "Accelerometer Tracker"
2. **Tap ▶️**: Start data collection (see real-time X,Y,Z values)
3. **Tap 📤**: Send data to phone
4. **On Phone**: App opens automatically showing received data
5. **Check Files**: CSV files saved in Documents folder

### 3. Verify CSV Output
**File Location:** `/Android/data/com.samsung.health.accelerometer.mobile/files/Documents/`  
**File Name:** `accelerometer_data_YYYYMMDD_HHMMSS.csv`  
**Format:**
```csv
timestamp,x,y,z,formatted_time
1693123456789,0.123,-9.456,2.789,2023-08-27 15:30:56.789
1693123456799,0.134,-9.445,2.801,2023-08-27 15:30:56.799
```

## Troubleshooting Common Issues

### Build Errors

**"JAVA_HOME is not set"**
```bash
# Download and install Java 11+ from https://adoptium.net/
# Or in Android Studio: File → Project Structure → SDK Location → JDK Location
```

**"SDK not found"**
```bash
# In Android Studio: Tools → SDK Manager
# Install: Android SDK 34, Build Tools 34.0.0
```

**"Gradle sync failed"**
```bash
# File → Invalidate Caches and Restart
# Build → Clean Project
# Build → Rebuild Project
```

### Device Connection Issues

**Samsung Galaxy Watch 4 not detected:**
```bash
# Ensure watch is paired with phone via Galaxy Watch app
# Enable Debug over Bluetooth on watch
# Restart Android Studio
# Try: Run → Edit Configurations → Target → Choose Connected Device
```

**Android Phone not detected:**
```bash
# Connect via USB cable
# Enable USB debugging on phone
# Accept debugging authorization popup
# Check: adb devices (should show device)
```

### Runtime Issues

**"Permission denied" errors:**
```bash
# On Watch: Grant Body Sensors permission
# On Phone: Grant Storage permissions
# Restart both apps after granting permissions
```

**"No accelerometer data":**
```bash
# Verify Samsung Health SDK integration
# Check Samsung Galaxy Watch 4 compatibility
# Ensure watch is not in power saving mode
# Check Logcat for sensor errors
```

**"Data not transferring":**
```bash
# Verify Bluetooth connection between devices
# Check Galaxy Watch app pairing status
# Restart both applications
# Check Logcat for Wearable API errors
```

### Performance Issues

**"Low sampling rate":**
```bash
# Close other sensor apps that might interfere
# Ensure watch has sufficient battery
# Check system performance in Logcat
```

**"App crashes":**
```bash
# View → Tool Windows → Logcat
# Filter by app package name
# Look for exception stack traces
# Check memory usage in Profiler
```

## Advanced Configuration

### Custom Sampling Rate
**File:** `wear/src/main/java/.../AccelerometerRepositoryImpl.kt`
```kotlin
// Change line ~85:
config["SamplingRate"] = 50 // Change from 100 to 50Hz
```

### Custom CSV Location
**File:** `mobile/src/main/java/.../CsvDataSaver.kt`
```kotlin
// Change line ~35:
val csvFile = File(context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), fileName)
```

### Debug Logging
Add to any file for debugging:
```kotlin
Log.d("DEBUG_TAG", "Debug message: $variable")
```

## Final Verification Checklist

- [ ] Project builds without errors
- [ ] Both APKs install successfully  
- [ ] Watch app shows real-time accelerometer data
- [ ] Data transfers from watch to phone
- [ ] CSV files are created with correct format
- [ ] Sampling rate is approximately 100Hz
- [ ] Files contain timestamp and accelerometer values

## Need Help?

**Check these locations for detailed logs:**
- **Android Studio**: View → Tool Windows → Logcat
- **Build Issues**: View → Tool Windows → Build  
- **Gradle Issues**: View → Tool Windows → Gradle

**Key log tags to filter by:**
- `AccelerometerRepositoryImpl`: Sensor data collection
- `MainViewModel`: App state management  
- `DataListenerService`: Data reception
- `CsvDataSaver`: File creation

The application is now ready for testing on Samsung Galaxy Watch 4!
