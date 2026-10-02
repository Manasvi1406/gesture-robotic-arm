# Contributing

1. Create a branch for your change.
2. Keep gesture mapping logic camera-independent and unit-testable.
3. Run `python -m pytest -q` before committing.
4. If changing the ROS 2 package, rebuild with `colcon build --symlink-install`.
5. Update documentation when changing commands, topics, ports or joint limits.
6. Do not commit generated `venv`, ROS build/install/log, or Unity Library files.
