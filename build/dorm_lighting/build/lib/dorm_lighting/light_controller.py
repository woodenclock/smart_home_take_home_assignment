import json
from datetime import datetime

import paho.mqtt.client as mqtt
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


MQTT_BROKER = "localhost"
MQTT_PORT = 1883

MQTT_COMMAND_TOPIC = "dorm/light/command"
MQTT_STATE_TOPIC = "dorm/light/state"


class LightController(Node):

    def __init__(self):
        super().__init__("light_controller")

        self.publisher_ = self.create_publisher(
            String,
            "light_state",
            10
        )

        self.current_state = "OFF"

        # MQTT setup
        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.mqtt_client.loop_start()

        # Check schedule every 30 seconds
        self.timer = self.create_timer(
            30.0,
            self.check_schedule
        )

        self.get_logger().info("Light controller started.")

    def on_connect(self, client, userdata, flags, rc):
        self.get_logger().info(f"Connected to MQTT broker with code {rc}")

        client.subscribe(MQTT_STATE_TOPIC)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()

        self.current_state = payload

        ros_msg = String()
        ros_msg.data = payload

        self.publisher_.publish(ros_msg)

        self.get_logger().info(
            f"Received light state from MQTT: {payload}"
        )

    def check_schedule(self):
        now = datetime.now()

        current_hour = now.hour
        current_minute = now.minute

        # Turn ON at 8:00 PM
        if current_hour == 20 and current_minute == 0:
            self.send_light_command("ON")

        # Turn OFF at 8:00 AM
        elif current_hour == 8 and current_minute == 0:
            self.send_light_command("OFF")

    def send_light_command(self, command):
        self.mqtt_client.publish(
            MQTT_COMMAND_TOPIC,
            command
        )

        self.current_state = command

        ros_msg = String()
        ros_msg.data = command

        self.publisher_.publish(ros_msg)

        self.get_logger().info(
            f"Sent MQTT command: {command}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = LightController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.mqtt_client.loop_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()