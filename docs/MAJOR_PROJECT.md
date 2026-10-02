# Major Project Scope

## Proposed title

**AI-Based Gesture-Controlled Robotic Arm Simulation Using Computer Vision and ROS 2**

## Problem statement

Traditional robotic-arm interfaces often require physical controllers or dedicated hardware. This project develops a software-only human-machine interface in which natural hand gestures are converted into robotic joint commands and visualized in a simulated environment.

## Objectives

- Detect hand landmarks in real time.
- Convert intuitive gestures into bounded joint commands.
- Publish commands through ROS 2.
- Visualize the robot using a URDF and RViz.
- Provide an optional Unity 3D simulation.
- Validate the system with automated and integration tests.

## Modules

1. Hand perception
2. Gesture mapping
3. Joint-state publishing
4. Robot description and visualization
5. Unity UDP visualization
6. Testing and CI

## Expected outcome

A user can control a simulated 4-DOF robotic arm and gripper using hand motion captured by a webcam, without physical robotic hardware.

## Evaluation metrics

- Gesture detection responsiveness
- Joint-command update rate
- Mapping consistency
- Lost-hand safety behavior
- End-to-end demonstration success
- Automated test pass rate

## Limitations

Hand depth is estimated from 2D landmark scale rather than a true depth sensor. Performance depends on lighting, camera placement and MediaPipe tracking quality. The Unity and RViz models are simulation representations rather than calibrated physical robots.
