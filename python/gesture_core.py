"""Gesture -> robot-arm joint mapping.

Pure-Python core shared by the standalone UDP bridge and the ROS 2 node.
The mapping logic (GestureMapper) has no heavy dependencies so it can be unit
tested without a camera. OpenCV / MediaPipe are imported lazily by HandTracker.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Optional, Sequence, Tuple

# MediaPipe hand landmark indices
WRIST, THUMB_TIP, INDEX_MCP, INDEX_TIP, MIDDLE_MCP, PINKY_MCP = 0, 4, 5, 8, 9, 17


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def norm(v: float, lo: float, hi: float) -> float:
    """Normalise v from [lo, hi] to [0, 1] (clamped)."""
    if hi == lo:
        return 0.0
    return clamp((v - lo) / (hi - lo), 0.0, 1.0)


@dataclass
class ArmState:
    """Joint targets. Angles in degrees, gripper 0 (closed) .. 1 (open)."""
    base_yaw: float = 0.0
    shoulder: float = 0.0
    elbow: float = 0.0
    wrist: float = 0.0
    gripper: float = 1.0
    tracking: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MappingConfig:
    active_min: float = 0.15          # usable part of the camera frame (x and y)
    active_max: float = 0.85
    base_range: Tuple[float, float] = (-90.0, 90.0)
    shoulder_range: Tuple[float, float] = (-70.0, 70.0)
    elbow_range: Tuple[float, float] = (0.0, 120.0)
    wrist_range: Tuple[float, float] = (-90.0, 90.0)
    scale_far: float = 0.10           # wrist->middle-MCP length when hand is far
    scale_near: float = 0.28          # ... and when it is close to the camera
    pinch_closed: float = 0.30        # thumb-index distance / hand scale => closed
    pinch_open: float = 1.00          # ... => fully open
    smoothing: float = 0.35           # EMA alpha, 1.0 = no smoothing


class GestureMapper:
    """Converts 21 hand landmarks (normalised image coords) into an ArmState.

    Gesture map
      hand left/right  -> base yaw
      hand up/down     -> shoulder (hand up = arm raises)
      hand near/far    -> elbow (near = extended, far = bent)
      hand tilt (roll) -> wrist rotation
      thumb-index pinch-> gripper (pinch = close)
    """

    def __init__(self, config: Optional[MappingConfig] = None):
        self.cfg = config or MappingConfig()
        self.state = ArmState()

    def reset(self) -> None:
        self.state = ArmState()

    def _target(self, lm: Sequence[Tuple[float, float]]) -> ArmState:
        c = self.cfg
        wx, wy = lm[WRIST]
        mx, my = lm[MIDDLE_MCP]
        scale = math.hypot(mx - wx, my - wy) or 1e-6

        # palm centre approximation: average of wrist and the 3 MCPs we have
        cx = (wx + mx + lm[INDEX_MCP][0] + lm[PINKY_MCP][0]) / 4.0
        cy = (wy + my + lm[INDEX_MCP][1] + lm[PINKY_MCP][1]) / 4.0

        tx = norm(cx, c.active_min, c.active_max)
        ty = norm(cy, c.active_min, c.active_max)
        ts = norm(scale, c.scale_far, c.scale_near)

        roll = math.degrees(math.atan2(mx - wx, -(my - wy)))  # 0 = fingers up

        ix, iy = lm[INDEX_TIP]
        px, py = lm[THUMB_TIP]
        pinch = math.hypot(ix - px, iy - py) / scale

        return ArmState(
            base_yaw=lerp(c.base_range[0], c.base_range[1], tx),
            shoulder=lerp(c.shoulder_range[0], c.shoulder_range[1], 1.0 - ty),
            elbow=lerp(c.elbow_range[1], c.elbow_range[0], ts),
            wrist=clamp(roll, *c.wrist_range),
            gripper=norm(pinch, c.pinch_closed, c.pinch_open),
            tracking=True,
        )

    def update(self, lm: Sequence[Tuple[float, float]]) -> ArmState:
        t = self._target(lm)
        a = self.cfg.smoothing
        if not self.state.tracking:          # first frame after (re)acquire: snap
            self.state = t
        else:
            s = self.state
            self.state = ArmState(
                base_yaw=lerp(s.base_yaw, t.base_yaw, a),
                shoulder=lerp(s.shoulder, t.shoulder, a),
                elbow=lerp(s.elbow, t.elbow, a),
                wrist=lerp(s.wrist, t.wrist, a),
                gripper=lerp(s.gripper, t.gripper, a),
                tracking=True,
            )
        return self.state

    def lost(self) -> ArmState:
        """No hand visible: hold the last pose, flag tracking False."""
        s = self.state
        self.state = ArmState(s.base_yaw, s.shoulder, s.elbow, s.wrist, s.gripper, False)
        return self.state


def demo_state(t: float) -> ArmState:
    """Synthetic motion for testing without a camera."""
    return ArmState(
        base_yaw=80 * math.sin(t * 0.6),
        shoulder=50 * math.sin(t * 0.9),
        elbow=60 + 55 * math.sin(t * 1.1),
        wrist=70 * math.sin(t * 1.5),
        gripper=0.5 + 0.5 * math.sin(t * 2.0),
        tracking=True,
    )


class HandTracker:
    """Webcam + MediaPipe Hands -> ArmState, with an annotated preview frame."""

    def __init__(self, camera: int = 0, width: int = 640, height: int = 480,
                 config: Optional[MappingConfig] = None):
        import cv2
        import mediapipe as mp

        self.cv2 = cv2
        self._hands_mod = mp.solutions.hands
        self._draw = mp.solutions.drawing_utils
        self.hands = self._hands_mod.Hands(
            max_num_hands=1, model_complexity=0,
            min_detection_confidence=0.6, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(camera)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {camera}")
        self.mapper = GestureMapper(config)

    def read(self):
        """Return (ArmState, annotated BGR frame) or (None, None) on camera failure."""
        cv2 = self.cv2
        ok, frame = self.cap.read()
        if not ok:
            return None, None
        frame = cv2.flip(frame, 1)  # mirror so on-screen motion matches your hand
        res = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if res.multi_hand_landmarks:
            hl = res.multi_hand_landmarks[0]
            state = self.mapper.update([(p.x, p.y) for p in hl.landmark])
            self._draw.draw_landmarks(frame, hl, self._hands_mod.HAND_CONNECTIONS)
        else:
            state = self.mapper.lost()
        self.draw_hud(frame, state)
        return state, frame

    def draw_hud(self, frame, s: ArmState) -> None:
        cv2 = self.cv2
        color = (0, 220, 0) if s.tracking else (0, 0, 255)
        lines = [
            f"{'TRACKING' if s.tracking else 'NO HAND'}",
            f"base    {s.base_yaw:7.1f} deg",
            f"shoulder{s.shoulder:7.1f} deg",
            f"elbow   {s.elbow:7.1f} deg",
            f"wrist   {s.wrist:7.1f} deg",
            f"gripper {s.gripper:7.2f}",
            "q / ESC: quit",
        ]
        for i, text in enumerate(lines):
            cv2.putText(frame, text, (10, 22 + 22 * i), cv2.FONT_HERSHEY_SIMPLEX,
                        0.55, color if i == 0 else (255, 255, 255), 2 if i == 0 else 1)

    def close(self) -> None:
        self.cap.release()
        self.hands.close()
