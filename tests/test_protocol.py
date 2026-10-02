import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from gesture_core import demo_state


def test_demo_state_is_json_serializable_and_bounded():
    payload = demo_state(1.0).to_dict()
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert set(decoded) == {"base_yaw", "shoulder", "elbow", "wrist", "gripper", "tracking"}
    assert -90 <= decoded["base_yaw"] <= 90
    assert -70 <= decoded["shoulder"] <= 70
    assert 0 <= decoded["elbow"] <= 120
    assert -90 <= decoded["wrist"] <= 90
    assert 0 <= decoded["gripper"] <= 1
    assert decoded["tracking"] is True
