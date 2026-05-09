import json
import paho.mqtt.client as mqtt     # mqtt python lib
import rclpy                        # ROS 2 client python lib
from rclpy.node import Node
from datetime import datetime
from std_msgs.msg import String


MQTT_BROKER = "localhost"
MQTT_PORT = 1883                            # Standard MQTT port
MQTT_COMMAND_TOPIC = "dorm/light/command"   # Tells light what to do
MQTT_STATE_TOPIC = "dorm/light/state"       # Reports current state


class LightController(Node):                        # Create a custom ROS node called LightController
                                                    # Inherits ROS2 node base class
    def __init__(self):                             # Object starts
        super().__init__("light_controller")        # Call parent ros node constructor, register node name

        self.publisher_ = self.create_publisher(    # Create ROS publisher node
            String,                                 # Publish string messages to ROS topic light_state
            "light_state",
            10                                      # Queue size 10
        )

        self.current_state = "OFF"                  # Stores current light status

        # MQTT setup
        self.mqtt_client = mqtt.Client()            # Create MQTT object, handles all MQTT operations

        self.mqtt_client.on_connect = self.on_connect   # When MQTT connects successfully, run self.on_connect()
        self.mqtt_client.on_message = self.on_message   # Whenever MQTT message arrives, run self.on_connect()
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)    # keep alive interval in secs
        self.mqtt_client.loop_start()                           # start MQTT background thread

        # Check schedule every 30 seconds
        self.timer = self.create_timer(
            30.0,
            self.check_schedule
        )
        self.get_logger().info("Light controller started.")    # Print out log to indicate start of operation

    def on_connect(self, client, userdata, flags, rc):  # Run automatically after successful MQTT connection
        self.get_logger().info(f"Connected to MQTT broker with code {rc}")  # rc = result code
        client.subscribe(MQTT_STATE_TOPIC)              # Receive any messages sent to dorm/light/state topic


    def on_message(self, client, userdata, msg):        # Runs whenever MQTT receives message
        payload = msg.payload.decode()                  # Message arrives in Bytes (e.g., b'ON' to "ON")
        self.current_state = payload                    # Update internal state
        ros_msg = String()                              # Create ROS string message
        ros_msg.data = payload                          # In which, store the payload text (e.g., "ON")
        self.publisher_.publish(ros_msg)                # Broadcast state into ROS ecosystem
        self.get_logger().info(                         # Log debugging info
            f"Received light state from MQTT: {payload}"
        )


    def check_schedule(self):       # Run every 30 secs
        now = datetime.now()        # Get current system time
        current_hour = now.hour     
        current_minute = now.minute

        # Turn ON at 8:00 PM
        if current_hour == 20 and current_minute == 0:
            self.send_light_command("ON")

        # Turn OFF at 8:00 AM
        elif current_hour == 8 and current_minute == 0:
            self.send_light_command("OFF")


    def send_light_command(self, command):      # Helper function to publish command
        self.mqtt_client.publish(
            MQTT_COMMAND_TOPIC,
            command
        )
        self.current_state = command            # Update internal state
        ros_msg = String()                      # Create ROS string message
        ros_msg.data = command                  # In which, store the payload text (e.g., "ON")
        self.publisher_.publish(ros_msg)        # Broadcast state into ROS ecosystem
        self.get_logger().info(                 # Log debugging info
            f"Sent MQTT command: {command}"
        )


def main(args=None):            # ROS entry point
    rclpy.init(args=args)       # Start ROS runtime
    node = LightController()    # Instantiate class

    try:
        rclpy.spin(node)        # Keep the node spinning/running

    except KeyboardInterrupt:
        pass

    finally:
        node.mqtt_client.loop_stop()    # Graceful exit
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()