## NTU Dorm Smart Lighting Automation 💡

At Nanyang Technological University (NTU), student dormitories are implementing energy-efficient automated room lighting.

### Current Challenges ⚠️
- Lights left ON overnight or during the day, wasting electricity
- Inconsistent usage habits across students
- No centralized management or automation

### Requirements ❔
The system must automatically:
- Turn lights **ON** at 8:00 PM (students return to rooms)
- Turn lights **OFF** at 8:00 AM (save daytime energy)

### Solution Architecture ⭐
The system is made of 3 main components:
- Philips Hue smart lights (Zigbee devices)
- MQTT broker for communication
- ROS 2 orchestration layer

The ROS 2 Node will publish the light commands such as send_light_command() through the MQTT Broker, which then relays the message to the light bulb, as shown in the diagram below. However, the ROS 2 Node also has to know the current state of the light bulb to make appropriate decisions, and for which the state information is sent in reverse order, which the ROS 2 Node receives through on_message().

COMMAND PATH:
ROS2 Controller Node
        |
        | MQTT publish
        v
MQTT Broker
        |
        v
Philips Hue Smart Light

STATE PATH:
Philips Hue Smart Light
        |
        | MQTT state update
        v
MQTT Broker
        |
        v
ROS2 Controller Node
        |
        | ROS2 publish
        v
ROS2 Subscribers













