FROM ros:humble-ros-base

SHELL ["/bin/bash", "-c"]

WORKDIR /ros2_ws

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY src ./src

RUN source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install

CMD source /opt/ros/humble/setup.bash && \
    source install/setup.bash && \
    ros2 run dorm_lighting light_controller