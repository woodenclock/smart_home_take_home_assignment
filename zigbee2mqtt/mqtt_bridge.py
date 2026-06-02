"""
MQTT Topic Bridge for Zigbee Smart Plug
Bridges Zigbee2MQTT topics to dorm/light topics
"""

import paho.mqtt.client as mqtt
import json
import os
import time

# Configuration
ZIGBEE_BASE_TOPIC = "zigbee2mqtt"
DORM_COMMAND_TOPIC = "dorm/light/command"
DORM_STATE_TOPIC = "dorm/light/state"
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# Smart plug friendly name (will be set after pairing)
SMART_PLUG_NAME = os.getenv("ZIGBEE_DEVICE_NAME", "smart_plug")

class MQTTBridge:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.plug_state = "OFF"
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"[Bridge] Connected to broker: {rc}")
        # Subscribe to Zigbee2MQTT device state
        client.subscribe(f"{ZIGBEE_BASE_TOPIC}/{SMART_PLUG_NAME}")
        # Subscribe to dorm commands
        client.subscribe(DORM_COMMAND_TOPIC)
        
    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic
        
        print(f"[Bridge] Received on {topic}: {payload}")
        
        # From dorm/light/command -> Zigbee2MQTT
        if topic == DORM_COMMAND_TOPIC:
            command = payload.strip().upper()
            if command in ["ON", "OFF"]:
                # Send to Zigbee device (state topic for commands)
                zigbee_payload = json.dumps({"state": command})
                client.publish(f"{ZIGBEE_BASE_TOPIC}/{SMART_PLUG_NAME}/set", zigbee_payload)
                print(f"[Bridge] Sent command {command} to {SMART_PLUG_NAME}")
        
        # From Zigbee device state -> dorm/light/state
        elif topic.startswith(ZIGBEE_BASE_TOPIC) and "/" + SMART_PLUG_NAME in topic:
            try:
                data = json.loads(payload)
                if "state" in data:
                    state = data["state"]
                    self.plug_state = state
                    client.publish(DORM_STATE_TOPIC, state)
                    print(f"[Bridge] Published state {state} to {DORM_STATE_TOPIC}")
            except json.JSONDecodeError:
                print(f"[Bridge] Failed to parse JSON: {payload}")
    
    def run(self):
        print(f"[Bridge] Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
        while True:
            try:
                self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
                break
            except OSError as exc:
                print(f"[Bridge] MQTT broker unavailable ({exc}); retrying in 2s")
                time.sleep(2)

        self.client.loop_forever()

if __name__ == "__main__":
    bridge = MQTTBridge()
    bridge.run()
