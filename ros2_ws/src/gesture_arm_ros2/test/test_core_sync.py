from pathlib import Path


def test_ros_core_matches_standalone_core():
    root = Path(__file__).resolve().parents[4]
    standalone = (root / "python" / "gesture_core.py").read_text()
    ros_copy = (root / "ros2_ws" / "src" / "gesture_arm_ros2" / "gesture_arm_ros2" / "gesture_core.py").read_text()
    assert standalone == ros_copy
