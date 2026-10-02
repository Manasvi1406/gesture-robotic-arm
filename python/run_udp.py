#!/usr/bin/env python3
"""Webcam hand gestures -> UDP JSON packets (consumed by the Unity simulation).

  python run_udp.py                 # webcam
  python run_udp.py --demo          # synthetic motion, no camera needed
"""
import argparse
import json
import socket
import time

import cv2

from gesture_core import HandTracker, demo_state


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--camera", type=int, default=0, help="camera index")
    ap.add_argument("--host", default="127.0.0.1", help="Unity host")
    ap.add_argument("--port", type=int, default=5005, help="Unity UDP port")
    ap.add_argument("--hz", type=float, default=60.0, help="max send rate")
    ap.add_argument("--no-preview", action="store_true", help="hide the camera window")
    ap.add_argument("--demo", action="store_true", help="send synthetic motion (no camera)")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (args.host, args.port)
    tracker = None if args.demo else HandTracker(camera=args.camera)
    period, t0 = 1.0 / args.hz, time.time()
    print(f"Sending to udp://{args.host}:{args.port}  (Ctrl+C to stop)")

    try:
        while True:
            start = time.time()
            if args.demo:
                state, frame = demo_state(start - t0), None
            else:
                state, frame = tracker.read()
                if state is None:
                    print("Camera read failed"); break
            sock.sendto(json.dumps(state.to_dict()).encode(), addr)

            if frame is not None and not args.no_preview:
                cv2.imshow("Gesture Controlled Robotic Arm", frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
            time.sleep(max(0.0, period - (time.time() - start)))
    except KeyboardInterrupt:
        pass
    finally:
        if tracker:
            tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
