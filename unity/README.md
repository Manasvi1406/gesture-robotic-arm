# Unity Simulation

This directory is a **complete minimal Unity project**, not only a scripts folder.

## Open

Open the `unity/` directory in Unity Hub. The project targets Unity **2022.3 LTS** and should also open in newer compatible Unity versions.

Open:

```text
Assets/Scenes/Main.unity
```

Press **Play**. `GestureArmBootstrap` automatically creates the floor, camera, light and robotic arm.

## Run without a webcam

From the repository root:

```bash
python python/run_udp.py --demo --host 127.0.0.1 --port 5005
```

The Unity arm should move continuously.

## Live control

```bash
python python/run_udp.py --camera 0 --host 127.0.0.1 --port 5005
```

## Architecture

```text
Python GestureMapper -> UDP/JSON -> GestureUdpReceiver -> GestureRobotArm
```

The Unity side is visualization-only; ROS 2 remains the robotics middleware path.

## UDP port

Default: `5005`.

If Unity reports a bind failure, close other applications using that port or change the port in both sender and receiver.
