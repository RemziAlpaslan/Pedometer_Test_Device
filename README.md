# Automated Pedometer Board Testing Device
This project is an automated testing system designed for pedometer electronic boards. The system simultaneously measures and records multiple parameters including current consumption, MQTT ID, and tilt sensor tests. All collected data is automatically written into a database for further analysis and traceability.

The project uses a Raspberry Pi, servo motors, Nordic PPK2 (Power Profiler Kit 2), and a display screen for user interaction and data visualization. A custom Python GUI is developed to control the testing workflow.

## Features
### Current Measurement:

Using Nordic PPK2 to measure precise current consumption during board operation.

### MQTT ID Testing:

Automatically verifies and logs MQTT IDs of the boards.

### Tilt Sensor Testing:

Tests the functionality of the onboard tilt sensor through controlled physical movements (using servo motors).

### Automated Database Logging:

All measured values and test results are saved automatically into a database system.

### Python GUI:

A user-friendly graphical interface to start tests, monitor progress, and display results live.

### Raspberry Pi Based:

Manages communication between all hardware components and runs the main control software.

## Hardware Used
Raspberry Pi 4

Nordic Semiconductor PPK2

Servo Motors

TFT Display / Touch Screen

Pedometer Electronic Boards

## Project Overview
The system is designed to:

Reduce manual effort and time required in testing pedometer boards.

Ensure standardized, accurate, and repeatable testing conditions.

Improve traceability by automatically storing each board’s performance data.

The workflow is fully automated, from hardware testing to data entry into the database, minimizing human errors.

## Future Improvements
Integration with remote cloud databases.

Adding automated error detection and test reporting features.

Enhancing GUI with real-time graphs and statistical summaries.
