import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from gesture_core import GestureMapper, MappingConfig, WRIST, MIDDLE_MCP, INDEX_MCP, PINKY_MCP, INDEX_TIP, THUMB_TIP


def hand(cx=0.5, cy=0.5, scale=0.19, pinch=1.0, roll_dx=0.0):
    """Synthetic 21-landmark hand. Fingers up, wrist at (cx, cy+scale)."""
    lm = [(cx, cy)] * 21
    lm = list(lm)
    lm[WRIST] = (cx, cy + scale)
    lm[MIDDLE_MCP] = (cx + roll_dx, cy)
    lm[INDEX_MCP] = (cx - 0.03, cy)
    lm[PINKY_MCP] = (cx + 0.03, cy)
    lm[THUMB_TIP] = (cx - 0.02, cy - 0.05)
    lm[INDEX_TIP] = (cx - 0.02 + pinch * scale, cy - 0.05)
    return lm


def fresh():
    return GestureMapper(MappingConfig(smoothing=1.0))


def test_centre_is_neutral():
    s = fresh().update(hand())
    assert abs(s.base_yaw) < 5 and s.tracking


def test_left_right_maps_to_base():
    m = fresh()
    assert m.update(hand(cx=0.1)).base_yaw < -80
    assert m.update(hand(cx=0.9)).base_yaw > 80


def test_up_raises_shoulder():
    m = fresh()
    assert m.update(hand(cy=0.2)).shoulder > m.update(hand(cy=0.8)).shoulder


def test_near_extends_elbow():
    m = fresh()
    assert m.update(hand(scale=0.30)).elbow < m.update(hand(scale=0.08)).elbow


def test_pinch_closes_gripper():
    m = fresh()
    assert m.update(hand(pinch=0.05)).gripper < 0.05
    assert m.update(hand(pinch=1.2)).gripper > 0.95


def test_roll_and_clamp():
    s = fresh().update(hand(roll_dx=0.5))
    assert 0 < s.wrist <= 90


def test_lost_holds_pose():
    m = fresh()
    a = m.update(hand(cx=0.8))
    b = m.lost()
    assert b.base_yaw == a.base_yaw and not b.tracking
