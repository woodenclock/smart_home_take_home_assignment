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

#### Architecture:
```
+--------------------------------------------------+
|                ROS 2 Lighting Node               |
|--------------------------------------------------|
| - Schedule automation (8PM ON / 8AM OFF)        |
| - MQTT publisher                                 |
| - MQTT subscriber                                |
| - ROS 2 topic publisher                          |
+------------------------+-------------------------+
                         |
                         | MQTT
                         v
+--------------------------------------------------+
|                 Mosquitto Broker                 |
+------------------------+-------------------------+
                         |
                         v
+--------------------------------------------------+
|           Smart Light / Device Simulator         |
|--------------------------------------------------|
| Receives ON/OFF MQTT commands                    |
| Publishes current light state                    |
+--------------------------------------------------+
```
#### Command Path:
```
ROS2 Controller Node
        |
        | MQTT publish
        v
MQTT Broker
        |
        v
Philips Hue Smart Light
```
#### State Path:
```
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
```

### 🔷 Prerequisites
* Ubuntu 22.04
* ROS 2 Humble
* Python 3.10+
* Mosquitto MQTT Broker

### 🔷 Installing Dependencies
In ubuntu bash, run the following command.
```
sudo apt update && sudo apt upgrade -y
```
Then, install ROS 2 Humble.
```
sudo apt install -y software-properties-common curl

sudo add-apt-repository universe -y

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update

sudo apt install -y ros-humble-ros-base python3-colcon-common-extensions python3-pip
```
Now source ROS 2 environment.
```
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

source ~/.bashrc
```
And install Python MQTT Library.
```
pip install paho-mqtt
```
And install Mosquito MQTT Broker.
```
sudo apt install -y mosquitto mosquitto-clients

sudo systemctl enable mosquitto

sudo systemctl start mosquitto
```
### 🔷 Building ROS 2 Package
Navigate to workspace, in my case, it is located in $/projects/smart_home_take_home_assignment.
```
cd ~/projects/smart_home_take_home_assignment
```
Then, build and source the workspace.
```
colcon build

source install/setup.bash
```
### 🔷 MQTT Topics
Before moving on, we'll take a look at the different topics for publishing and subscribing.
<br/>
<br/>
**Command Topic**: Used to send ON/OFF commands to the smart light.
```
dorm/light/command
```
**State Topic**: Used by the light device to publish its current state.
```
dorm/light/state
```
### 🔷 Running MQTT Broker
Verify Mosquitto is running.
```
sudo systemctl status mosquitto
```
Expected Output:
```
active (running)
```
### 🔷 Running ROS 2 Node
Run the following commands:
```
cd ~/projects/smart_home_take_home_assignment

source install/setup.bash

ros2 run dorm_lighting light_controller
```
Expected Output:
```
[INFO] Light controller started.
```
### 🔷 Testing ON / OFF commands.
**Terminal 1: Run ROS 2 Node**
```
ros2 run dorm_lighting light_controller
```
**Terminal 2: Moniter ROS 2 Topic**
```
source ~/projects/smart_home_take_home_assignment/install/setup.bash

ros2 topic echo /light_state
```
**Terminal 3: Publish MQTT State**
```
mosquitto_pub -h localhost -t dorm/light/state -m "ON"

mosquitto_pub -h localhost -t dorm/light/state -m "OFF"
```
Expected Output:
```
data: ON

data: OFF
```
### 🔷 Testing MQTT broker.
We will use different terminals to simulate the different components of the architecture.
<br/>
<br/>
**Terminal 1: Subscriber**
```
mosquitto_sub -h localhost -t test/topic
```
**Terminal 2: Publisher**
```
mosquitto_pub -h localhost -t test/topic -m "hello"
```
Expected Output:
```
hello
```
### 🔷 Possible Future Improvements
* Philips Hue API integration
* Docker containerization
* Unit and integration tests
* Dynamic scheduling parameters

#### Author: Lee Sungmin
For any problems/suggestions, please contact the author at `luckyisland3710@gmail.com`.
