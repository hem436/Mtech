# Accelerometer Data Transfer App for Samsung Galaxy Watch 4

This application transfers accelerometer data from a Samsung Galaxy Watch 4 to a mobile phone at 100Hz sampling rate and saves the data as CSV files with timestamps.

## Features

- **High-frequency data collection**: Collects accelerometer data at 100Hz sampling rate
- **Real-time data transfer**: Transfers data from watch to mobile via Bluetooth
- **CSV file export**: Automatically saves received data to CSV files with timestamps
- **User-friendly interface**: Simple start/stop controls on watch, data visualization on mobile
- **Automatic file naming**: CSV files are named with timestamps for easy organization

## Architecture

The app consists of three modules:

### 1. Common Module
- Shared data structures (`AccelerometerData`)
- Serializable data classes for communication

### 2. Wear Module (Samsung Galaxy Watch 4)
- Accelerometer data collection using Samsung Health Sensor SDK
- Real-time data processing at 100Hz
- Bluetooth data transmission to mobile
- Clean UI with start/stop/send controls

### 3. Mobile Module (Android Phone)
- Receives data from watch via Wearable API
- Automatically saves data to CSV files
- Displays received data with visualization
- File management in Documents folder

## Setup Instructions

### Prerequisites
1. Samsung Galaxy Watch 4 or compatible Samsung smartwatch
2. Android phone with Galaxy Watch app installed
3. Both devices paired via Galaxy Watch app
4. Android Studio for development

### Installation
1. Clone this repository
2. Open in Android Studio
3. Build and install both wear and mobile APKs
4. Grant necessary permissions (sensors, storage)

### Usage
1. **On Watch**: Open "Accelerometer Tracker" app
2. **Start Collection**: Tap the play button to start collecting data
3. **Monitor Data**: View real-time X, Y, Z accelerometer values
4. **Transfer Data**: Tap the send button to transfer collected data to phone
5. **On Phone**: Data is automatically saved to CSV files in Documents folder

## Data Format

The CSV files contain the following columns:
- `timestamp`: Unix timestamp in milliseconds
- `x`: X-axis acceleration (m/s²)
- `y`: Y-axis acceleration (m/s²)  
- `z`: Z-axis acceleration (m/s²)
- `formatted_time`: Human-readable timestamp

Example:
```csv
timestamp,x,y,z,formatted_time
1693123456789,0.123,-9.456,2.789,2023-08-27 15:30:56.789
1693123456799,0.134,-9.445,2.801,2023-08-27 15:30:56.799
```

## File Locations

CSV files are saved to:
`/Android/data/com.samsung.health.accelerometer.mobile/files/Documents/accelerometer_data_YYYYMMDD_HHMMSS.csv`

## Technical Details

### Sampling Rate
- Target: 100Hz (100 samples per second)
- Actual rate may vary based on system load and hardware capabilities

### Data Collection
- Uses Samsung Health Sensor SDK for accelerometer access
- Continuous data collection when tracking is active
- Automatic data buffering and batch transfer

### Communication
- Uses Google Wearable API for watch-to-phone communication
- JSON serialization for data transfer
- Automatic reconnection on connection loss

## Permissions Required

### Watch App
- `BODY_SENSORS`: Access to accelerometer
- `WAKE_LOCK`: Keep screen on during data collection

### Mobile App  
- `WRITE_EXTERNAL_STORAGE`: Save CSV files
- `READ_EXTERNAL_STORAGE`: Access saved files

## Troubleshooting

### Common Issues
1. **No data appearing**: Ensure both apps have proper permissions
2. **Connection failed**: Check Bluetooth connection and Galaxy Watch app pairing
3. **Files not saving**: Verify storage permissions on mobile app
4. **Low sampling rate**: Close other sensor apps that might interfere

### Debug Information
- Check Android logs for detailed error messages
- Monitor connection status in both apps
- Verify CSV file creation in Documents folder

## Development Notes

### Key Components
- `AccelerometerRepositoryImpl`: Handles Samsung Health SDK integration
- `MessageRepository`: Manages watch-to-phone communication
- `CsvDataSaver`: Handles file creation and data persistence
- `MainViewModel`: Coordinates data flow and UI state

### Customization Options
- Modify sampling rate in `AccelerometerRepositoryImpl`
- Adjust data buffer size (`maxValuesToKeep`)
- Change CSV file location in `CsvDataSaver`
- Customize UI in respective MainActivity files

## License

Licensed under the Apache License, Version 2.0. See LICENSE file for details.

## Support

For issues related to Samsung Health SDK, consult Samsung Health Developer documentation.
For general Android development questions, refer to Android Developer documentation.
