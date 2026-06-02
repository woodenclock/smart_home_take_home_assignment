# Zigbee Smart Plug Integration - Quick Start Guide

## Overview

This guide walks you through integrating a real Zigbee smart device (smart plug, smart bulb, etc.) with the dorm lighting automation system using a Zigbee USB dongle.

## What You'll Need

1. **Zigbee USB Dongle** (e.g., CC2531, ConBee II, Sonoff ZBDongle)
2. **Zigbee Smart Device** (Philips Hue, IKEA TRADFRI, smart plug, etc.)
3. **Ubuntu Machine** with Docker installed
4. **USB Port** to connect the dongle

## Step-by-Step Setup

### 1. Plug in Your Zigbee USB Dongle

Connect the Zigbee USB dongle to your Ubuntu machine.

### 2. Detect the USB Device

Run the detection script:

```bash
cd ~/smart_home_take_home_assignment
chmod +x setup_zigbee.sh
./setup_zigbee.sh detect
```

Example output:
```
ℹ️  Detecting Zigbee USB devices...
ℹ️  Found USB devices:
  - /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_01234567-if00-port0 -> /dev/ttyUSB0
ℹ️  Also found direct ttyUSB devices:
  - /dev/ttyUSB0
```

Note down your device path. If it's different from `/dev/ttyUSB0`, update `docker-compose.yml`.

### 3. Update Docker Compose (if needed)

If your device is not `/dev/ttyUSB0`, edit `docker-compose.yml`:

```yaml
services:
  zigbee2mqtt:
    devices:
      - /dev/ttyACM0:/dev/ttyACM0  # Change to your actual device
```

### 4. Start Docker Services

```bash
./setup_zigbee.sh start
```

This will:
- Pull the latest Docker images
- Build the ROS 2 project image
- Start mosquitto, zigbee2mqtt, and lighting_controller containers
- Display service status

### 5. Access Zigbee2MQTT Web Interface

Open your browser and go to:
```
http://localhost:8080
```

You should see the Zigbee2MQTT interface with your USB adapter detected.

### 6. Pair Your Smart Device

**Method 1: Using Web Interface (Easiest)**

1. In the Zigbee2MQTT UI, look for a button like **"Permit join (All)"** or **"Add device"**
2. Click to enable pairing mode (usually lasts 254 seconds)
3. Reset/Power-cycle your smart device to put it into pairing mode
   - Most devices: Hold power button for 3-5 seconds
   - Check device manual for specific instructions
4. Wait for the device to appear in the UI under **"Devices"**

**Method 2: Using Terminal**

Monitor pairing in terminal:
```bash
docker compose logs -f zigbee2mqtt
```

Watch for log messages like: `Device has joined the network`

### 7. Set Device Friendly Name

After pairing, you'll see a device ID (like `0x00158d00045a1234`).

1. Click on the device in the UI
2. Set a friendly name (e.g., `smart_plug`, `bedroom_light`)
3. Save the configuration

### 8. Test Your Device

**Terminal 1: Monitor device state**
```bash
mosquitto_sub -h localhost -t "zigbee2mqtt/smart_plug/state"
```

**Terminal 2: Send ON command**
```bash
mosquitto_pub -h localhost -t "zigbee2mqtt/smart_plug/set" -m '{"state":"ON"}'
```

**Expected result:** 
- The physical device should turn ON
- You should see state changes in Terminal 1:
  ```json
  {"state":"ON","power":1.5,"energy":12345,"voltage":220,"current":7}
  ```

**Terminal 3: Send OFF command**
```bash
mosquitto_pub -h localhost -t "zigbee2mqtt/smart_plug/set" -m '{"state":"OFF"}'
```

### 9. Verify ROS 2 Integration

Check that the ROS 2 lighting controller is running:

```bash
docker compose logs -f lighting_controller
```

You should see:
```
[INFO] Light controller started.
```

### 10. Test Scheduled Automation

The lights will automatically turn:
- **ON at 8:00 PM** - watch MQTT topic: `dorm/light/command`
- **OFF at 8:00 AM**

Monitor in terminal:
```bash
mosquitto_sub -h localhost -t "dorm/light/command"
```

## Troubleshooting

### USB Device Not Found

**Problem:** `ls /dev/ttyUSB*` shows nothing

**Solution:**
1. Check USB cable connection
2. Try different USB port
3. Install USB drivers: `sudo apt install -y usb-modeswitch libusb-1.0-0`

### Permission Denied on USB Device

**Problem:** `docker: Error response from daemon ... permission denied`

**Solution:**
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
docker compose down && docker compose up -d
```

### Device Pairs but Doesn't Respond

**Problem:** Device shows in UI but commands don't work

**Solution:**
1. Check device supports Zigbee 3.0 (most devices do)
2. Try re-pairing the device
3. Check device batteries (if wireless)
4. Review device manual for correct command format

### Zigbee2MQTT Won't Start

**Problem:** `docker compose logs -f zigbee2mqtt` shows errors

**Common causes:**
- Wrong USB device path
- USB device already in use by another process
- Unsupported Zigbee adapter

**Check logs:**
```bash
docker compose logs zigbee2mqtt
```

### No Connection Between Services

**Problem:** Lighting controller can't reach MQTT

**Solution:**
```bash
# Verify all containers are on the same network
docker network inspect dorm_network

# Rebuild services
docker compose down
docker compose up -d
```

## Advanced Topics

### Using Multiple Smart Devices

1. Pair multiple devices (repeat Step 6)
2. Set unique friendly names for each
3. Monitor all devices:
   ```bash
   mosquitto_sub -h localhost -t "zigbee2mqtt/#"
   ```

### Persistent Configuration

Device pairing data is stored in:
```
./zigbee2mqtt/data/
```

This data persists across container restarts.

### Backup Configuration

```bash
# Backup
tar -czf zigbee_backup.tar.gz zigbee2mqtt/data/

# Restore
tar -xzf zigbee_backup.tar.gz
docker compose restart zigbee2mqtt
```

### Remove All Pairings

To reset and start fresh:

```bash
docker compose down -v  # Removes all volumes
docker compose up -d
# Re-pair all devices
```

## Quick Command Reference

```bash
# Setup
./setup_zigbee.sh detect              # Detect USB device
./setup_zigbee.sh check               # Check Docker installation

# Control
./setup_zigbee.sh start               # Start all services
./setup_zigbee.sh stop                # Stop all services
./setup_zigbee.sh logs                # View live logs
./setup_zigbee.sh status              # Check service status

# MQTT Testing
mosquitto_sub -h localhost -t "zigbee2mqtt/smart_plug/state"
mosquitto_pub -h localhost -t "zigbee2mqtt/smart_plug/set" -m '{"state":"ON"}'

# Docker
docker compose ps                     # Show running containers
docker compose logs -f zigbee2mqtt    # Follow Zigbee2MQTT logs
docker compose restart               # Restart all services
docker compose down                  # Stop and remove containers
```

## Next Steps

1. Integrate with your home automation dashboard
2. Set up multiple smart devices
3. Create automations based on different schedules
4. Monitor energy consumption

## Support

For issues with:
- **Zigbee2MQTT**: Visit https://www.zigbee2mqtt.io/
- **MQTT**: Check mosquitto documentation
- **ROS 2**: See main README.md

## References

- Zigbee2MQTT Documentation: https://www.zigbee2mqtt.io/
- Supported Devices: https://www.zigbee2mqtt.io/supported-devices/
- Zigbee Adapters: https://www.zigbee2mqtt.io/guide/adapters/

---

**Happy automating! 🏠💡**
