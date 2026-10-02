# System Architecture

## Layers

1. **Perception** — OpenCV captures frames; MediaPipe detects one hand and produces 21 normalized landmarks.
2. **Gesture mapping** — `GestureMapper` converts landmarks into bounded joint targets and applies smoothing.
3. **Transport** — ROS 2 publishes `sensor_msgs/JointState`; optional UDP sends the same state to Unity.
4. **Robot model** — URDF defines links, joints, axes and limits.
5. **Visualization** — RViz renders the ROS model; Unity renders an interactive 3D simulation.

## Data contract

```text
ArmState
  base_yaw   degrees [-90, 90]
  shoulder   degrees [-70, 70]
  elbow      degrees [0, 120]
  wrist      degrees [-90, 90]
  gripper    normalized [0, 1]
  tracking   boolean
```

ROS converts the four angular values to radians and maps gripper opening to two symmetric prismatic joints.

## Design principles

- Camera-independent core logic
- Deterministic demo mode
- Explicit joint limits
- Hold-last-pose behavior when tracking is lost
- No hardware dependency
- Testable boundaries between perception and control
