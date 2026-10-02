"""ROS 2 node for gesture-controlled robotic arm.

Modes:
  demo=True       -> synthetic motion
  udp_input=True  -> receive ArmState JSON from an external sender
  otherwise       -> use the local camera/MediaPipe tracker

The UDP input mode is intended for Windows webcam -> WSL ROS 2 setups.
"""

import json
import math
import socket
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from .gesture_core import ArmState, HandTracker, demo_state

FINGER_TRAVEL = 0.03


class GestureNode(Node):
    def __init__(self) -> None:
        super().__init__("gesture_arm_node")

        self.declare_parameter("camera_index", 0)
        self.declare_parameter("rate_hz", 30.0)
        self.declare_parameter("show_preview", True)
        self.declare_parameter("demo", False)

        # UDP input: Windows -> WSL ROS 2
        self.declare_parameter("udp_input", False)
        self.declare_parameter("udp_input_host", "0.0.0.0")
        self.declare_parameter("udp_input_port", 5005)

        # UDP output: ROS 2 -> Unity
        self.declare_parameter("udp_enabled", False)
        self.declare_parameter("udp_host", "127.0.0.1")
        self.declare_parameter("udp_port", 5005)

        p = self.get_parameter

        self.demo = bool(p("demo").value)
        self.udp_input = bool(p("udp_input").value)
        self.show_preview = bool(p("show_preview").value) and not self.demo

        # UDP input receiver
        self.input_sock = None
        if self.udp_input:
            host = str(p("udp_input_host").value)
            port = int(p("udp_input_port").value)

            self.input_sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
            self.input_sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )
            self.input_sock.bind((host, port))
            self.input_sock.setblocking(False)

            self.get_logger().info(
                f"UDP input listening on {host}:{port}"
            )

        # UDP output receiver for Unity, preserved from original project
        self.udp_addr = (
            str(p("udp_host").value),
            int(p("udp_port").value)
        )
        self.sock = (
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if bool(p("udp_enabled").value)
            else None
        )

        # Local camera mode
        self.tracker = None
        if not self.demo and not self.udp_input:
            self.tracker = HandTracker(
                camera=int(p("camera_index").value)
            )

        self.cv2 = self.tracker.cv2 if self.tracker else None

        self.last_udp_state = None
        self.last_udp_log = 0.0

        self.pub = self.create_publisher(
            JointState,
            "joint_states",
            10
        )

        self.t0 = time.time()

        self.create_timer(
            1.0 / float(p("rate_hz").value),
            self.tick
        )

        if self.demo:
            mode = "demo"
        elif self.udp_input:
            mode = "UDP input"
        else:
            mode = "camera"

        self.get_logger().info(
            f"gesture_arm_node started ({mode}) -> /joint_states"
        )

    def receive_udp_state(self):
        """Receive one ArmState JSON packet without blocking."""
        if self.input_sock is None:
            return None

        try:
            data, _addr = self.input_sock.recvfrom(4096)
        except BlockingIOError:
            return self.last_udp_state
        except OSError as exc:
            self.get_logger().error(
                f"UDP receive error: {exc}"
            )
            return self.last_udp_state

        try:
            payload = json.loads(data.decode("utf-8"))

            required = (
                "base_yaw",
                "shoulder",
                "elbow",
                "wrist",
                "gripper",
            )

            if not all(key in payload for key in required):
                self.get_logger().warning(
                    "Received UDP packet missing required ArmState fields"
                )
                return self.last_udp_state

            state = ArmState(
                base_yaw=float(payload["base_yaw"]),
                shoulder=float(payload["shoulder"]),
                elbow=float(payload["elbow"]),
                wrist=float(payload["wrist"]),
                gripper=float(payload["gripper"]),
            )

            self.last_udp_state = state
            return state

        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.get_logger().warning(
                f"Invalid UDP packet: {exc}"
            )
            return self.last_udp_state

    def tick(self) -> None:
        if self.demo:
            state = demo_state(time.time() - self.t0)
            frame = None

        elif self.udp_input:
            state = self.receive_udp_state()
            frame = None

            if state is None:
                return

        else:
            state, frame = self.tracker.read()

            if state is None:
                self.get_logger().error(
                    "Camera read failed",
                    throttle_duration_sec=2.0
                )
                return

        self.publish(state)

        # Optional ROS 2 -> Unity UDP output
        if self.sock:
            self.sock.sendto(
                json.dumps(state.to_dict()).encode(),
                self.udp_addr
            )

        if frame is not None and self.show_preview:
            self.cv2.imshow(
                "Gesture Controlled Robotic Arm",
                frame
            )

            if self.cv2.waitKey(1) & 0xFF in (
                ord("q"),
                27
            ):
                rclpy.shutdown()

    def publish(self, s: ArmState) -> None:
        opening = s.gripper * FINGER_TRAVEL

        msg = JointState()

        msg.header.stamp = (
            self.get_clock().now().to_msg()
        )

        msg.name = [
            "joint_base",
            "joint_shoulder",
            "joint_elbow",
            "joint_wrist",
            "finger_left_joint",
            "finger_right_joint",
        ]

        msg.position = [
            math.radians(s.base_yaw),
            math.radians(s.shoulder),
            math.radians(s.elbow),
            math.radians(s.wrist),
            opening,
            opening,
        ]

        self.pub.publish(msg)

    def destroy_node(self) -> bool:
        if self.tracker:
            self.tracker.close()

        if self.cv2:
            self.cv2.destroyAllWindows()

        if self.input_sock:
            self.input_sock.close()

        if self.sock:
            self.sock.close()

        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)

    node = GestureNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
