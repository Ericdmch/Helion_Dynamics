# CanSat Challenge 2025

Welcome to our repository for the **CanSat Challenge 2025**. This project aims to design, build, and launch a CanSat (a simulation of a satellite) that will collect environmental data during its descent from an altitude of approximately 1 km. The goal is to demonstrate an efficient design and provide accurate data collection for a variety of conditions.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Team Members](#team-members)
3. [System Architecture](#system-architecture)
4. [Components](#components)
5. [Data Collection & Analysis](#data-collection--analysis)
6. [Launch and Testing Plan](#launch-and-testing-plan)
7. [Installation](#installation)
8. [Usage](#usage)
9. [Contributing](#contributing)
10. [License](#license)

---

## Project Overview

Our CanSat will be launched from a rocket and descend via parachute, collecting data on its environment, including temperature, pressure, altitude, and location. We aim to achieve a smooth descent while transmitting real-time data to our ground station.

### Objectives:
- Accurately measure altitude, temperature, and pressure.
- Transmit real-time data to the ground station during descent.
- Land safely while protecting the internal components.

## Team Members

- **Eric Chen** - Electronics and Communication Lead

- **Emerson Yu** - Electronics and Communication Lead

- **Laura Wang** - Something

- **Felix Chen** - Something

- **Abigail Wang** - Something

## System Architecture

The CanSat is composed of several subsystems:

- **Power System**: Provides energy to all onboard components.
- **Sensor System**: Collects environmental data such as pressure, temperature, and altitude using a variety of sensors (e.g., BME680, GPS).
- **Communication System**: A LoRa-based system is used to transmit data in real-time to the ground station.
- **Descent System**: Includes a parachute for controlled descent and an impact absorption mechanism.

## Components

- **Microcontroller**: iLabs RP2040 Challenger LoRa
- **Sensors**: Adafruit BME680 (pressure, temperature, humidity, gas sensor), GPS sensor
- **Power Source**: LiPo battery
- **Communication**: LoRa communication module for real-time data transmission
- **Descent System**: Custom-designed parachute for controlled descent

## Data Collection & Analysis

The data collected by the CanSat will include:

- **Altitude**: Measured using barometric pressure.
- **Temperature**: Recorded throughout the descent.
- **Pressure**: Atmospheric pressure data to correlate with altitude.
- **GPS Coordinates**: Used to track the descent path.

The data will be processed and analyzed to determine the CanSat’s performance and environmental conditions during the flight.

## Launch and Testing Plan

1. **Prototype Construction**: Assemble and test all components.
2. **Ground Testing**: Perform sensor calibration and communication tests.
3. **Drop Tests**: Simulate the CanSat's descent from various altitudes.
4. **Final Launch**: Participate in the CanSat Challenge 2025, launching the CanSat and collecting data from an altitude of ~1 km.

## Installation

To set up the software on your local machine:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourteam/cansat-challenge-2025.git
   cd cansat-challenge-2025
