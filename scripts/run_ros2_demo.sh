#!/usr/bin/env bash
set -euo pipefail
source /opt/ros/jazzy/setup.bash
cd "$(dirname "$0")/../ros2_ws"
source install/setup.bash
ros2 launch gesture_arm_ros2 display.launch.py demo:=true
