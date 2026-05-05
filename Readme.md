## Problem Statement: NTU Dorm Smart Lighting Automation

At Nanyang Technological University (NTU), student dormitories are implementing energy-efficient automated room lighting.

### Current Challenges
- Lights left ON overnight or during the day, wasting electricity
- Inconsistent usage habits across students
- No centralized management or automation

### Solution Stack
- Philips Hue smart lights (Zigbee devices)
- MQTT broker for communication
- ROS 2 orchestration layer

## Your Task

Build a ROS 2 Python package that acts as a scheduled lighting controller for a dorm room.

### Requirements
The system must automatically:
- Turn lights **ON** at 8:00 PM (students return to rooms)
- Turn lights **OFF** at 8:00 AM (save daytime energy)

### Node Responsibilities
- Send commands to the light via MQTT
- Receive current light state from MQTT
- Publish light state into ROS 2
