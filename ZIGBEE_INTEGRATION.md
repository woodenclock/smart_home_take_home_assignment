# Zigbee Integration Changes Summary

## Overview

This document outlines all modifications made to integrate Zigbee USB dongle and smart plug support with the dorm lighting automation system.

## Files Modified

### 1. `docker-compose.yml` ✅ UPDATED
- Added `zigbee2mqtt` service
- Added `dorm_network` bridge network
- Added USB device passthrough: `/dev/ttyUSB0:/dev/ttyUSB0`
- Updated all services to use the `dorm_network`
- Added dependencies between services

**Key additions:**
```yaml
zigbee2mqtt:
  image: koenkk/zigbee2mqtt:latest
  devices:
    - /dev/ttyUSB0:/dev/ttyUSB0
  volumes:
    - ./zigbee2mqtt/data:/app/data
    - ./zigbee2mqtt/configuration.yaml:/app/configuration.yaml
```

### 2. `Readme.md` ✅ UPDATED
- Added comprehensive Zigbee section with:
  - Updated architecture diagram showing Zigbee2MQTT bridge
  - Prerequisites for Zigbee devices
  - Step-by-step setup instructions
  - Device pairing guide
  - MQTT topic testing examples
  - Troubleshooting section
  - Docker Compose quick commands
  - Integration notes for light controller

## Files Created

### 1. `zigbee2mqtt/configuration.yaml` ✨ NEW
Zigbee2MQTT configuration file that:
- Defines USB device port: `/dev/ttyUSB0`
- Configures MQTT broker connection: `mqtt://mosquitto:1883`
- Sets up frontend UI on port 8080
- Configures Zigbee network settings (PAN ID, channels)

### 2. `zigbee2mqtt/data/` (directory) ✨ NEW
- Persistent volume for storing:
  - Device pairing data
  - Network configuration
  - Device state snapshots

### 3. `zigbee2mqtt/mqtt_bridge.py` ✨ NEW
Python MQTT bridge script for mapping:
- `dorm/light/command` → `zigbee2mqtt/{device}/set`
- `zigbee2mqtt/{device}/state` → `dorm/light/state`

**Note:** This is optional; can also manually use Zigbee2MQTT topics directly.

### 4. `setup_zigbee.sh` ✨ NEW
Bash helper script with commands:
- `detect` - Find Zigbee USB dongle
- `check` - Verify Docker installation
- `start` - Launch all Docker services
- `stop` - Stop services
- `logs` - View live logs
- `status` - Show service status

Usage:
```bash
chmod +x setup_zigbee.sh
./setup_zigbee.sh detect
./setup_zigbee.sh start
```

### 5. `.env.example` ✨ NEW
Environment variable template for easy configuration:
- MQTT_BROKER
- MQTT_PORT
- ZIGBEE_DEVICE
- ZIGBEE_DEVICE_NAME
- TZ (Timezone)
- LOG_LEVEL

### 6. `ZIGBEE_QUICKSTART.md` ✨ NEW
Complete quick-start guide with:
- Requirements checklist
- Step-by-step setup instructions
- Device pairing procedures
- Testing examples
- Troubleshooting guide
- Advanced topics (multiple devices, backups)
- Command reference

## Architecture Changes

### Before (Simulator Only)
```
ROS 2 Controller → MQTT Broker ← Simulator
```

### After (With Real Zigbee Device)
```
ROS 2 Controller → MQTT Broker
                      ↓
                 Zigbee2MQTT
                      ↓
              USB Dongle ↔ Smart Device
```

## Docker Network Changes

All services now communicate via a bridge network `dorm_network`:
- `mosquitto` - MQTT broker
- `zigbee2mqtt` - Zigbee bridge
- `lighting_controller` - ROS 2 node

Network ensures reliable service-to-service communication.

## MQTT Topics Overview

### Original Topics (for ROS controller)
- Command: `dorm/light/command`
- State: `dorm/light/state`

### Zigbee2MQTT Topics
- State: `zigbee2mqtt/{device_name}`
- Set command: `zigbee2mqtt/{device_name}/set`
- Bridge: `zigbee2mqtt/bridge/state`

### Data Format
- **ROS Topics:** Plain text (`ON`, `OFF`)
- **Zigbee2MQTT:** JSON objects
  ```json
  {"state":"ON", "power":1.5, "energy":12345}
  ```

## How It Works

1. **Device Pairing:**
   - Enable pairing mode in Zigbee2MQTT UI
   - Reset Zigbee smart device
   - Zigbee2MQTT discovers and registers the device

2. **Command Flow:**
   - ROS controller publishes `ON`/`OFF` to `dorm/light/command`
   - Optional bridge converts to `{"state":"ON"}` on `zigbee2mqtt/device/set`
   - Zigbee2MQTT sends Zigbee command to device
   - Device updates its state

3. **State Feedback:**
   - Smart device publishes state to Zigbee2MQTT
   - Zigbee2MQTT converts to MQTT on `zigbee2mqtt/device`
   - Optional bridge converts to `dorm/light/state`
   - ROS controller receives and publishes on ROS topic `/light_state`

## Configuration Options

### USB Device Path
If dongle is at `/dev/ttyACM0` instead of `/dev/ttyUSB0`, update:
```yaml
# docker-compose.yml
zigbee2mqtt:
  devices:
    - /dev/ttyACM0:/dev/ttyACM0
```

### Zigbee Network Settings
Edit `zigbee2mqtt/configuration.yaml`:
```yaml
advanced:
  pan_id: 0x1a62          # Personal Area Network ID
  ext_pan_id: [...]       # Extended PAN ID
  channel: 11             # Zigbee channel (11-26)
  channel_mask: [11]      # Allowed channels
```

### Device Mapping
Once paired, rename device in UI to use friendly names:
- `smart_plug` → `zigbee2mqtt/smart_plug`
- `bedroom_light` → `zigbee2mqtt/bedroom_light`

## Supported Zigbee Adapters

Zigbee2MQTT supports these USB adapters:
- **TI CC2531** - Popular, cheaper option
- **TI CC2538** - Better range
- **ConBee II** - Excellent compatibility
- **Sonoff ZBDongle** - XIAO variant
- **RaspBee** - For Raspberry Pi

## Next Steps

1. ✅ Update docker-compose.yml with Zigbee2MQTT service
2. ✅ Create Zigbee2MQTT configuration
3. ✅ Create setup helper scripts
4. ✅ Update documentation
5. ⏭️ **Test with actual hardware** (your next step!)

## Testing Checklist

- [ ] USB dongle detected: `./setup_zigbee.sh detect`
- [ ] Docker services start: `./setup_zigbee.sh start`
- [ ] Zigbee2MQTT UI accessible: `http://localhost:8080`
- [ ] Smart device paired successfully
- [ ] Can send ON/OFF commands via MQTT
- [ ] ROS controller receives state updates
- [ ] Scheduled automation runs at 8 PM and 8 AM

## Troubleshooting Resources

- **Zigbee2MQTT Docs:** https://www.zigbee2mqtt.io/
- **Supported Devices:** https://www.zigbee2mqtt.io/supported-devices/
- **Docker Troubleshooting:** See ZIGBEE_QUICKSTART.md
- **MQTT Testing:** Use `mosquitto_sub` and `mosquitto_pub` utilities

## Version Info

- **Zigbee2MQTT:** Latest stable (koenkk/zigbee2mqtt:latest)
- **Mosquitto:** 2.x (eclipse-mosquitto:2)
- **ROS 2:** Humble
- **Python:** 3.10+

## Important Notes

⚠️ **USB Device Permissions:**
If you get permission errors, run:
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
```

⚠️ **Port Conflicts:**
- 1883 (MQTT): Ensure local mosquitto is stopped
- 8080 (Zigbee2MQTT UI): Ensure no other service uses this port

⚠️ **Device Path Variability:**
USB device paths can change. Use `/dev/serial/by-id/` for consistent naming:
```bash
ls /dev/serial/by-id/
# Use this path in docker-compose.yml for stability
```

## Success Indicators

When everything is working:

```bash
# Service status
$ docker compose ps
CONTAINER ID        STATUS
xxx                 Up X minutes (mosquitto)
xxx                 Up X minutes (zigbee2mqtt)
xxx                 Up X minutes (lighting_controller)

# Device state visible
$ mosquitto_sub -h localhost -t "zigbee2mqtt/smart_plug"
{"state":"ON", "power":1.5, ...}

# ROS controller running
$ docker compose logs lighting_controller
[INFO] Light controller started.
```

## Additional Resources

- Full documentation: [Readme.md](Readme.md)
- Quick start guide: [ZIGBEE_QUICKSTART.md](ZIGBEE_QUICKSTART.md)
- Project root: [smart_home_take_home_assignment/](.)

---

**Status:** ✅ Zigbee integration complete and ready for testing!

**Next:** Run `./setup_zigbee.sh start` to begin using with your physical Zigbee devices.
