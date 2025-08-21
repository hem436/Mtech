@echo off
echo Building Accelerometer Data Transfer App...

echo.
echo Building common module...
call gradlew :common:build

echo.
echo Building wear module...
call gradlew :wear:build

echo.
echo Building mobile module...
call gradlew :mobile:build

echo.
echo Build complete! 
echo.
echo To install:
echo 1. Connect Samsung Galaxy Watch 4
echo 2. Run: gradlew :wear:installDebug
echo 3. Connect Android phone  
echo 4. Run: gradlew :mobile:installDebug
echo.
pause
