#!/usr/bin/env bash

set -e

PROJECT="$HOME/gesture-robotic-arm"
ROS_WS="$PROJECT/ros2_ws"

source /opt/ros/jazzy/setup.bash
source "$ROS_WS/install/setup.bash"

echo "=========================================="
echo " Gesture Controlled Robotic Arm"
echo " ROS 2 + RViz UDP Receiver"
echo "=========================================="
echo
echo "Listening for Windows webcam data..."
echo "UDP port: 5005"
echo

cd "$ROS_WS"

ros2 launch gesture_arm_ros2 display.launch.py \
    udp_input:=true \
    udp_input_host:=0.0.0.0 \
    udp_input_port:=5005 \
    demo:=false \
    show_preview:=false
