# CanSat Challenge 2025

Welcome to our repository for the **CanSat Challenge 2025**. This project aims to design, build, and launch a CanSat (a simulation of a satellite) that will collect environmental data during its descent from an altitude of approximately 1 km. The goal is to demonstrate an efficient design and provide accurate data collection for a variety of conditions.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Team Members](#team-members)
3. [Components](#components)
4. [Data Collection & Analysis](#data-collection--analysis)
5. [Launch and Testing Plan](#launch-and-testing-plan)
6. [Installation](#installation)


---

## Project Overview

Our CanSat will be launched from a rocket and descend via parachute, collecting data on its environment, including temperature, pressure, altitude, and location. We aim to achieve a smooth descent while transmitting real-time data to our ground station. 

Our secondary mission, in short, is to quantify the stress response of algae due to the affects of g-force, temperature and pressure, as it ascends in a rocket and descends onto exterrestial planets for space missions.

### Objectives:
- Accurately measure altitude, temperature, and pressure.
- Transmit real-time data to the ground station during descent.
- Land safely while protecting the internal components.

## Team Members

- **Eric Chen** - Mechanical Engineer

- **Emerson Yu** - Electronics and Software Engineer

- **Laura Wang** - Team Manager

- **Felix Chen** - Head of Outreach 

- **Abigail Wang** - Head of Mission Research

## Components

- **Microcontroller**: Raspberry Pi Pico, Teensy 4.0
- **Sensors**: Adafruit BME680 (pressure, temperature, humidity, gas sensor), GPS PA1010D
- **Power Source**: LiPo battery 3.7V, 9V Battery
- **Communication**: LoRa communication module for real-time data transmission, DX-LR02
- **Descent System**: Custom-designed parachute for controlled descent

## Data Collection & Analysis

The data collected by the CanSat will include:

- **Temperature**: Recorded throughout the descent.
- **Pressure**: Atmospheric pressure data to correlate with altitude.
- **GPS Coordinates**: Used to track the descent path.
- **Fluorometer Data**: Measurement of stress upon algae

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
   git clone https://github.com/Ericdmch/Helion_Dynamics.git
   cd Helion_Dynamics

**Important Source Links**

[OPEN-JIP](https://github.com/HarveyBates/Open-JIP)

