# Excel Integration and Data Visualization Enhancement

This document describes the enhancements made to the Teensy Data Logger application to support Excel integration and data visualization.

## New Features

### Excel Integration
- Automatic creation of formatted Excel workbooks
- Real-time updates to Excel files as data is collected
- Multiple worksheet organization:
  - Sensor Data sheet with all raw data
  - Dashboard sheet with summary statistics and key visualizations
  - Environmental Graphs sheet for temperature, humidity, pressure, and gas data
  - Motion Graphs sheet for acceleration and gyroscope data
  - Light Graphs sheet for photodiode data

### Data Visualization
- Automatic generation of graphs using matplotlib:
  - Temperature over time
  - Humidity over time
  - Pressure over time
  - Gas resistance over time
  - Combined environmental dashboard
  - Acceleration (X, Y, Z) over time
  - Gyroscope readings (X, Y, Z) over time
  - 3D acceleration plot
  - Light level over time
- Graphs are saved as PNG files and embedded in the Excel workbook
- Real-time dashboard with latest readings and statistics

## Requirements

The enhanced logger requires additional Python packages:
- openpyxl - For Excel file creation and manipulation
- matplotlib - For graph generation
- pandas - For data handling and analysis

Install these packages using pip:
```
pip install openpyxl matplotlib pandas
```

## Usage

The enhanced logger works the same way as the original version but with additional Excel and graph functionality:

```
python teensy_data_logger_excel.py
```

Optional arguments:
- `-p, --port PORT` - Specify serial port to connect to
- `-b, --baud BAUD` - Specify baud rate (default: 115200)
- `-d, --directory DIR` - Specify log directory (default: logs)
- `-l, --list` - List available serial ports

## Output Files

The enhanced logger creates the following files:
- `logs/sensor_data.csv` - CSV file with all sensor data
- `logs/sensor_data.json` - JSON file with all sensor data
- `logs/sensor_data.xlsx` - Excel workbook with data and graphs
- `logs/graphs/` - Directory containing all generated graph images

## Excel Workbook Structure

The Excel workbook contains the following sheets:

1. **Sensor Data** - Contains all raw data in a tabular format with proper headers and formatting.

2. **Dashboard** - Contains:
   - Summary statistics (min, max, average values)
   - Latest sensor readings
   - Combined environmental graph for quick overview

3. **Environmental Graphs** - Contains:
   - Temperature over time graph
   - Humidity over time graph
   - Pressure over time graph

4. **Motion Graphs** - Contains:
   - Acceleration (X, Y, Z) over time graph
   - Gyroscope readings (X, Y, Z) over time graph
   - 3D acceleration plot

5. **Light Graphs** - Contains:
   - Light level over time graph

## Customization

The Excel update frequency can be adjusted by changing the `excel_update_interval` variable in the `TeensyDataLogger` class. By default, the Excel file is updated every 10 data points to balance performance and real-time updates.

## Performance Considerations

- Excel file generation and graph creation can be resource-intensive
- For very long data collection sessions, consider increasing the `excel_update_interval`
- For systems with limited resources, you may want to disable automatic graph generation during data collection and generate them only at the end

## Troubleshooting

- If you encounter "Permission denied" errors when saving Excel files, ensure you have write permissions to the logs directory
- If graphs are not appearing in the Excel file, check that the graph directory exists and that matplotlib is properly installed
- For large datasets, Excel file generation may take longer; be patient during updates
