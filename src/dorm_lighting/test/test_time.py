import time
import rclpy
from datetime import datetime, timedelta
from dorm_lighting.light_controller import LightController
from dorm_lighting.system_clock import FakeClock


# Start at 7:59 PM
fake_time = datetime(2026, 1, 1, 19, 58, 0)
clock = FakeClock(fake_time)

rclpy.init()
node = LightController(clock=clock)

print("Starting simulation...")

try:
    for i in range(5):
        clock.fixed_datetime += timedelta(minutes=1)

        node.check_schedule()

        print("Current fake time:", clock.now())

        time.sleep(1)

finally:
    node.mqtt_client.loop_stop()
    node.destroy_node()
    rclpy.shutdown()