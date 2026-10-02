# Testing Guide

## Level 1 — Unit tests

```bash
source venv/bin/activate
python -m pytest -q
```

Covers center, left/right, vertical movement, depth mapping, pinch, wrist roll and lost-hand behavior.

## Level 2 — UDP demo

Start the sender:

```bash
python python/run_udp.py --demo --host 127.0.0.1 --port 5005
```

The sender must remain active and emit JSON packets at the configured rate.

## Level 3 — ROS 2 build

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

Expected: `1 package finished`.

## Level 4 — ROS 2 synthetic integration

```bash
ros2 launch gesture_arm_ros2 display.launch.py demo:=true
```

In a second terminal:

```bash
ros2 topic echo /joint_states --once
```

Expected: six joint names and six positions.

## Level 5 — Unity synthetic integration

Open `unity/` in Unity, open `Assets/Scenes/Main.unity`, press Play, then run the Python UDP demo.

## Level 6 — Live webcam

Run the Python or ROS camera mode and verify that each gesture produces the intended joint motion. Test in good lighting and with one hand visible.

## Pass criteria

- All unit tests pass.
- ROS 2 package builds without errors.
- `/joint_states` is published in demo mode.
- RViz renders the URDF.
- Unity receives UDP state in demo mode.
- Live camera mode detects a hand and updates the state.
