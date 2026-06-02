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
### 🔷 Project Structure
```
smart_home_take_home_assignment/
├── src/
│  └── dorm_lighting/
│    ├── dorm_lighting/
│    │   ├── init.py
│    │   ├── light_controller.py
│    │   └── system_clock.py
│    ├── test/
│    │   └── test_time.py
│    ├── LICENSE
│    ├── package.xml
│    ├── setup.py
│    └── setup.cfg
├── build/
├── install/
└── log/
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
And install and run Mosquito MQTT Broker.
```
sudo apt install -y mosquitto mosquitto-clients

sudo systemctl enable mosquitto

sudo systemctl start mosquitto
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
### 🔷 Testing MQTT broker (Optional)
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
This confirms that the local MQTT broker can receive and forward messages.
### 🔷 Testing ON / OFF commands
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
This proves that:
* The MQTT broker is working.
* The ROS 2 node receives MQTT state messages.
* The ROS 2 node publishes the received light state to `/light_state`.

### 🔷 Testing Scheduled ON / OFF Automation with Fake Clock

The lighting controller is required to automatically:

- Turn lights **ON at 8:00 PM**
- Turn lights **OFF at 8:00 AM**

Waiting until the actual system time reaches 8:00 PM or 8:00 AM is not practical during development. To solve this, the project uses a small clock abstraction.

The real node uses `SystemClock`, which reads the actual system time.<br/>
For testing, `FakeClock` is used to simulate different times immediately.<br/>
This makes the schedule logic deterministic and easy to test.

#### Test File

The scheduled automation test is located at: `src/dorm_lighting/test/test_time.py`<br/>
The test creates a fake time, passes it into the `LightController`, and manually advances time minute by minute.

**Terminal 1: Subscriber**
```
mosquitto_sub -h localhost -t dorm/light/command
```
**Terminal 2: Publisher**
```
python3 src/dorm_lighting/test/test_time.py
```

When the fake time reaches `20:00`, the node should publish: `ON`.

Change the `fake_time` in `test_time.py` from `19` to `7`.<br/>
When the fake time reaches `08:00`, the node should publish: `OFF`.

### 🔷 Running through Docker

Note: If Mosquitto is already running locally on the host machine, port 1883 may conflict with the Docker Mosquitto container. Stop the local broker before testing Docker:

```
sudo systemctl stop mosquitto
```

### 🔷 Zigbee Integration with Physical Devices

This project now includes **Zigbee2MQTT** bridge support for controlling real Zigbee devices (e.g., Philips Hue smart plugs) via the Zigbee USB dongle.

#### Architecture with Zigbee

```
+------------------------------------------+
|          ROS 2 Lighting Node             |
+------------------------------------------+
              |
              | MQTT (dorm/light/command, dorm/light/state)
              v
+------------------------------------------+
|        Mosquitto MQTT Broker             |
+------------------------------------------+
              |
              | MQTT (zigbee2mqtt/*)
              v
+------------------------------------------+
|      Zigbee2MQTT Bridge Service          |
|  Translates MQTT <-> Zigbee Protocol    |
+------------------------------------------+
              |
              | Zigbee Protocol
              v
+------------------------------------------+
|   Zigbee USB Dongle + Smart Devices     |
|  (Smart Plugs, Philips Hue lights, etc.) |
+------------------------------------------+
```

#### Prerequisites for Zigbee

1. **Zigbee USB Dongle** - Supported adapters: CC2531, CC2538, ConBee II, Sonoff ZBDongle, etc.
2. **Zigbee Smart Device** - Philips Hue bulb, IKEA TRADFRI, Gledopto, or compatible device
3. **Docker** - For containerized deployment
4. **Docker Compose** - For multi-service orchestration

#### Setup Steps

**Step 1: Identify the USB Dongle**

On Ubuntu, plug in your Zigbee USB dongle and identify its device:

```bash
ls /dev/serial/by-id/
```

You should see something like:
```
usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_01234567-if00-port0
```

Or simply:
```bash
ls /dev/ttyUSB*
```

**Step 2: Update Docker Compose (if device path is different)**

Edit `docker-compose.yml` and update the `zigbee2mqtt` service `devices` section:

```yaml
devices:
  - /dev/ttyUSB0:/dev/ttyUSB0  # Change to your actual device
```

**Step 3: Start Docker Services**

```bash
cd ~/projects/smart_home_take_home_assignment

docker compose up -d
```

Verify all services are running:

```bash
docker compose ps
```

Expected output:
```
CONTAINER ID   IMAGE                           STATUS
xxxxx          eclipse-mosquitto:2             Up X minutes
xxxxx          koenkk/zigbee2mqtt:latest       Up X minutes
xxxxx          dorm-lighting-controller        Up X minutes
```

**Step 4: Access Zigbee2MQTT Frontend**

Open your browser and navigate to:
```
http://localhost:8080
```

You should see the Zigbee2MQTT UI. The USB adapter should be detected.

**Step 5: Pair Your Zigbee Device**

1. In the Zigbee2MQTT UI, click **"Permit join (All)"** to enable pairing mode (lasts 254 seconds)
2. Power on or reset your Zigbee smart device to pairing mode
   - Most devices: Hold the power/pairing button for 3-5 seconds
   - Some devices may have a reset button
3. Wait for the device to appear in the UI under **"Devices"**

**Step 6: Configure Device Friendly Name**

1. Once paired, the device appears in the UI
2. Click on the device and set a friendly name (e.g., `smart_plug`)
3. Device will now publish to: `zigbee2mqtt/smart_plug/state`

**Step 7: Create MQTT Bridge (Optional)**

If you want the Zigbee device to respond to `dorm/light/command` topic directly, create a simple MQTT bridge.

Create a new service in `docker-compose.yml` or use `zigbee2mqtt/mqtt_bridge.py` to map topics.

For now, the device will respond to:
- **Publish commands to**: `zigbee2mqtt/{device_name}/set` with payload `{"state":"ON"}` or `{"state":"OFF"}`
- **Subscribe to state**: `zigbee2mqtt/{device_name}` (publishes full device state)

#### Testing Zigbee Device

**Terminal 1: Monitor device state**
```bash
mosquitto_sub -h localhost -t "zigbee2mqtt/smart_plug"
```

**Terminal 2: Send command**
```bash
mosquitto_pub -h localhost -t "zigbee2mqtt/smart_plug/set" -m '{"state":"ON"}'

mosquitto_pub -h localhost -t "zigbee2mqtt/smart_plug/set" -m '{"state":"OFF"}'
```

You should see the physical device turn ON/OFF and state updates in Terminal 1.

#### Troubleshooting

**Device not found after pairing:**
- Check Zigbee2MQTT logs: `docker compose logs -f zigbee2mqtt`
- Ensure permit join is enabled before pairing
- Try resetting the device and pairing again

**USB device permission denied:**
```bash
sudo usermod -a -G dialout $USER
# Then log out and log back in
```

**Cannot connect to Mosquitto:**
- Verify mosquitto container is running: `docker compose ps`
- Check MQTT broker logs: `docker compose logs -f mosquitto`

#### Docker Compose Quick Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f                    # All services
docker compose logs -f zigbee2mqtt        # Zigbee2MQTT only
docker compose logs -f lighting_controller

# Stop services
docker compose down

# Rebuild images
docker compose build

# Clean up volumes (remove paired devices)
docker compose down -v
```

### 🔷 Integration with Light Controller

The ROS 2 light controller can be extended to use Zigbee2MQTT topics directly:

Update `light_controller.py` to subscribe/publish to:
- **State topic**: `zigbee2mqtt/{device_name}` (parse `"state"` field)
- **Command topic**: `zigbee2mqtt/{device_name}/set` (send `{"state":"ON/OFF"}`)

Or keep the current `dorm/light/*` topics and add a separate bridge service to translate between them.

### 🔷 Possible Future Improvements
* Native Zigbee2MQTT to dorm/light/* MQTT bridge
* Web dashboard for device management
* Multi-device support (multiple smart plugs)
* Advanced scheduling with sunrise/sunset
* Energy consumption monitoring
* Unit and integration tests
* Kubernetes deployment

#### Author: Lee Sungmin
For any problems/suggestions, please contact the author at `luckyisland3710@gmail.com`.
