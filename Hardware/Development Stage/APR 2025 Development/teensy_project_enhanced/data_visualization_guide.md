# Data Visualization Guide

This document explains the data visualization capabilities implemented in the enhanced Teensy Data Logger application.

## Graph Types

### Environmental Data Graphs
1. **Temperature Graph**
   - Displays temperature readings over time
   - Red line plot showing temperature in °C
   - Useful for monitoring temperature trends and fluctuations

2. **Humidity Graph**
   - Displays humidity readings over time
   - Blue line plot showing relative humidity in %
   - Helps track humidity changes in the environment

3. **Pressure Graph**
   - Displays atmospheric pressure readings over time
   - Green line plot showing pressure in hPa
   - Useful for weather monitoring and altitude estimation

4. **Gas Resistance Graph**
   - Displays gas resistance readings over time
   - Yellow line plot showing resistance in kOhms
   - Higher resistance typically indicates cleaner air

5. **Combined Environmental Dashboard**
   - 2x2 grid of all environmental parameters
   - Compact view of all BME680 sensor data
   - Provides a quick overview of all environmental conditions

### Motion Data Graphs
1. **Acceleration Graph**
   - Displays acceleration readings over time
   - Three lines (red, green, blue) for X, Y, and Z axes
   - Measured in g (gravitational force)
   - Useful for monitoring movement and orientation changes

2. **Gyroscope Graph**
   - Displays angular velocity readings over time
   - Three lines (red, green, blue) for X, Y, and Z axes
   - Measured in degrees per second (°/s)
   - Useful for tracking rotation and orientation changes

3. **3D Acceleration Plot**
   - 3D scatter plot showing the relationship between X, Y, and Z acceleration
   - Points colored by time sequence (newer points in different colors)
   - Provides spatial visualization of movement patterns
   - Limited to the most recent 100 data points for clarity

### Light Data Graph
1. **Light Level Graph**
   - Displays photodiode readings over time
   - Yellow line plot showing raw light level values
   - Useful for monitoring ambient light conditions

## Graph Generation Process

1. Data is collected from the Teensy 4.1 receiver via serial connection
2. At regular intervals (every 10 data points by default), graphs are generated
3. Matplotlib creates and saves each graph as a PNG file in the `logs/graphs` directory
4. Graphs are embedded in the Excel workbook in their respective sheets
5. The dashboard sheet includes the combined environmental graph for quick reference

## Customizing Graphs

The graph generation code is modular and can be easily customized:

- To change graph colors, modify the color parameters in the plot functions
- To change graph sizes, modify the `figsize` parameters
- To add new graph types, create new functions following the existing pattern
- To change the update frequency, modify the `excel_update_interval` variable

## Interpreting the Graphs

### Environmental Data
- **Temperature**: Normal room temperature is typically 20-25°C
- **Humidity**: Comfortable humidity is usually 30-60%
- **Pressure**: Standard atmospheric pressure at sea level is approximately 1013.25 hPa
- **Gas Resistance**: Higher values indicate cleaner air (less volatile organic compounds)

### Motion Data
- **Acceleration**: When stationary, Z-axis should show approximately 1g (gravity)
- **Gyroscope**: When stationary, all axes should be close to 0°/s
- **3D Plot**: A stationary sensor will show points clustered in one area

### Light Data
- The photodiode provides raw analog values (0-1023)
- Higher values indicate brighter conditions
- The actual meaning of values depends on the specific photodiode module used

## Technical Implementation

The graphs are generated using the following Python libraries:
- **matplotlib**: For creating the plots and visualizations
- **pandas**: For data manipulation and preparation
- **openpyxl**: For embedding the graphs in Excel

The graph generation process is designed to be efficient and non-blocking, allowing data collection to continue uninterrupted while graphs are being created.
