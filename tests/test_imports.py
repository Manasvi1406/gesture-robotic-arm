import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_core_imports_without_camera():
    import gesture_core
    assert hasattr(gesture_core, "GestureMapper")
    assert hasattr(gesture_core, "demo_state")
