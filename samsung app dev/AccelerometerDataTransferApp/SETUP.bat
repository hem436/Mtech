@echo off
echo ================================================================
echo   Android Studio Build & Run Setup for Accelerometer App
echo ================================================================
echo.

echo Step 1: Check Java Installation
echo --------------------------------
where java >nul 2>nul
if %errorlevel% equ 0 (
    echo ✓ Java found in PATH
    java -version
) else (
    echo ✗ Java not found in PATH
    echo Please install Java 11+ or set JAVA_HOME
    echo Download from: https://adoptium.net/
    pause
    exit /b 1
)

echo.
echo Step 2: Open Project in Android Studio
echo --------------------------------------
echo 1. Open Android Studio
echo 2. File → Open
echo 3. Navigate to: %cd%
echo 4. Click OK and wait for Gradle sync
echo.

echo Step 3: Device Setup Required
echo -----------------------------
echo Samsung Galaxy Watch 4:
echo   - Enable Developer Options (tap Software version 7 times)
echo   - Enable ADB debugging
echo   - Enable Debug over Bluetooth
echo.
echo Android Phone:
echo   - Enable Developer Options (tap Build number 7 times)  
echo   - Enable USB debugging
echo   - Install Galaxy Watch app and pair with watch
echo.

echo Step 4: Build & Install
echo -----------------------
echo In Android Studio:
echo   1. Build → Clean Project
echo   2. Build → Rebuild Project
echo   3. Run → Edit Configurations
echo      - Create config for 'wear' module → Samsung Galaxy Watch 4
echo      - Create config for 'mobile' module → Android Phone
echo   4. Click Run ▶️ for each module
echo.

echo Alternative Command Line Build:
echo   gradlew clean build
echo   gradlew :wear:installDebug
echo   gradlew :mobile:installDebug
echo.

echo Step 5: Testing
echo --------------
echo Watch App: "Accelerometer Tracker"
echo   - Tap ▶️ to start data collection
echo   - View real-time X, Y, Z values
echo   - Tap 📤 to send data to phone
echo.
echo Mobile App: "Accelerometer Data Receiver"  
echo   - Receives data automatically
echo   - Data saved to CSV files in Documents folder
echo   - File format: accelerometer_data_YYYYMMDD_HHMMSS.csv
echo.

echo ================================================================
echo Ready to build! Open Android Studio and follow the steps above.
echo ================================================================
pause
