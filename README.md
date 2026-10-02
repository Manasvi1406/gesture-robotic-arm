# AI-Based Gesture-Controlled Robotic Arm Simulation

A **hardware-free final-year major project** that converts real-time hand gestures into robotic-arm joint commands and visualizes the result in **ROS 2 + RViz** and optionally **Unity**.

## 1. Project objective

The system uses a webcam to detect one hand with **MediaPipe Hands + OpenCV**, maps the 21 hand landmarks to a bounded 4-DOF arm plus gripper state, and publishes the result through a common joint-state interface.

```text
Webcam
  │
  ▼
OpenCV + MediaPipe
  │  21 landmarks
  ▼
GestureMapper
  │  4 joint angles + gripper + tracking state
  ├──────────────► ROS 2 /joint_states ─► robot_state_publisher ─► RViz
  │
  └──────────────► UDP JSON ─► Unity 3D simulation
```

### Why this is suitable as a major project

- Real-time computer vision and human-computer interaction
- Robotics kinematics/control interface through joint targets
- ROS 2 node, URDF model, launch system and RViz visualization
- Optional Unity visualization over a documented UDP protocol
- Deterministic demo mode for testing without a camera
- Automated unit tests and GitHub Actions CI
- Clear separation between perception, mapping, transport and visualization
- No physical hardware required

## 2. Main features

| Feature | Implementation |
|---|---|
| Hand detection | MediaPipe Hands |
| Image processing | OpenCV |
| Gesture-to-joint mapping | Python `GestureMapper` |
| Base rotation | Hand X position |
| Shoulder | Hand Y position |
| Elbow | Apparent hand depth/scale |
| Wrist | Hand roll |
| Gripper | Thumb-index pinch |
| Smoothing | Exponential moving average |
| Lost-hand behavior | Hold last pose |
| ROS 2 output | `sensor_msgs/JointState` |
| Robot model | URDF |
| Visualization | RViz2 + optional Unity |
| Unity transport | UDP/JSON |
| Test mode | Synthetic demo motion |
| CI | GitHub Actions |

## 3. Repository structure

```text
gesture-robotic-arm/
├── .github/workflows/           # CI
├── config/                      # documented motion/protocol defaults
├── docs/                        # architecture, testing and major-project docs
├── python/                      # camera perception + gesture mapping + UDP
├── ros2_ws/
│   └── src/gesture_arm_ros2/    # ROS 2 ament_python package
├── tests/                       # Python unit/protocol tests
├── unity/                       # self-contained Unity project + scripts
├── scripts/                     # repeatable setup/test commands
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── LICENSE
└── README.md
```

## 4. Prerequisites

### Python / computer vision

- Python 3.10–3.12
- Webcam for live mode
- OpenCV
- MediaPipe 0.10.14
- NumPy < 2

### ROS 2

- ROS 2 Jazzy recommended
- `rviz2`
- `robot_state_publisher`
- `rclpy`
- `sensor_msgs`
- `launch` / `launch_ros`
- `colcon`

### Unity (optional)

- Unity 2021.3 LTS or newer
- Built-in Render Pipeline
- The repository contains a complete minimal Unity project; no manual scene construction is required.

## 5. Quick start — Python tests

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
```

Expected result:

```text
7 passed
```

The test suite is deliberately independent of a webcam.

## 6. Python demo mode

Demo mode generates deterministic synthetic arm motion and does not require a camera:

```bash
source venv/bin/activate
python python/run_udp.py --demo --host 127.0.0.1 --port 5005
```

Press `Ctrl+C` to stop.

For live hand tracking:

```bash
python python/run_udp.py --camera 0
```

Use `--camera 1` if the default webcam is not available.

## 7. ROS 2 + RViz

**Recommended approach:** use the ROS 2 environment for the ROS package and install the computer-vision Python dependencies into the same Python environment used by the ROS node.

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### Synthetic demo — no webcam

```bash
ros2 launch gesture_arm_ros2 display.launch.py demo:=true
```

Then, in another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 topic echo /joint_states --once
```

### Live webcam

```bash
ros2 launch gesture_arm_ros2 display.launch.py demo:=false camera_index:=0
```

Useful arguments:

```text
demo:=true/false
camera_index:=0
rviz:=true/false
show_preview:=true/false
rate_hz:=30
udp_enabled:=true/false
udp_host:=127.0.0.1
udp_port:=5005
```

## 8. ROS 2 interfaces

### Published topic

`/joint_states` — `sensor_msgs/msg/JointState`

Joint order:

```text
joint_base
joint_shoulder
joint_elbow
joint_wrist
finger_left_joint
finger_right_joint
```

### Robot description

The URDF is installed from:

```text
ros2_ws/src/gesture_arm_ros2/urdf/gesture_arm.urdf
```

## 9. Unity integration

The `unity/` directory is a complete minimal Unity project. Open the `unity` folder in Unity Hub.

Open:

```text
Assets/Scenes/Main.unity
```

Press **Play**.

Start the Python UDP bridge:

```bash
python python/run_udp.py --demo --host 127.0.0.1 --port 5005
```

The simulated arm should move continuously. For live control, replace `--demo` with camera mode.

### UDP packet

UTF-8 JSON is sent at the configured rate. Example schema:

```json
{
  "base_yaw": 0.0,
  "shoulder": 0.0,
  "elbow": 60.0,
  "wrist": 0.0,
  "gripper": 1.0,
  "tracking": true
}
```

Angles are degrees. `gripper` is normalized from `0.0` (closed) to `1.0` (open).

## 10. Gesture mapping

| Gesture | Target |
|---|---|
| Move hand left/right | Base yaw |
| Move hand up/down | Shoulder pitch |
| Move hand closer/farther | Elbow |
| Rotate/tilt hand | Wrist |
| Thumb + index pinch | Gripper |
| No hand detected | Hold previous pose |

All joint targets are clamped to the corresponding robot limits.

## 11. Validation status

The repository is designed so each layer can be validated independently:

1. **Unit tests** — gesture mapping without camera
2. **Demo transport** — synthetic UDP stream without camera
3. **ROS 2 build** — `colcon build --symlink-install`
4. **RViz demo** — synthetic `/joint_states`
5. **Unity demo** — synthetic UDP motion
6. **Live integration** — webcam → MediaPipe → mapper → ROS/Unity

The live webcam test depends on the user's camera and desktop environment, so it must be performed on the target machine.

## 12. Troubleshooting

### Pytest loads an incompatible ROS plugin

Use a compatible pytest version from `requirements-dev.txt`. The project intentionally keeps pytest below version 9 because ROS 2 Jazzy's `launch_testing` plugin can be incompatible with pytest 9.

### Camera cannot open

```bash
python python/run_udp.py --camera 1
```

Close applications already using the webcam. If WSL does not expose the webcam, run the Python live component in Windows Python instead or use the ROS/Unity demo mode for software-only validation.

### RViz shows an empty view

Confirm:

```bash
ros2 topic list
ros2 topic echo /joint_states --once
```

and ensure RViz Fixed Frame is `base_link`.

### Unity shows NO SIGNAL

Confirm the Python sender and Unity receiver use the same UDP port (default `5005`) and that both use `127.0.0.1` for local testing.

## 13. Academic major-project deliverables

Recommended final demonstration:

1. Start ROS 2 + RViz in demo mode.
2. Show the robot model and changing `/joint_states`.
3. Start Unity and demonstrate the UDP simulation.
4. Switch to webcam mode.
5. Demonstrate each gesture and explain the mapping.
6. Show automated test results.
7. Explain system architecture, limitations and future hardware integration.

## 14. Future scope

- Multi-hand gesture control
- Gesture classification using a trained ML model
- Collision detection and self-collision constraints
- MoveIt 2 integration for planning
- Gazebo simulation with physics
- Object manipulation tasks
- Voice + gesture multimodal control
- Physical robotic-arm deployment

## License

MIT
