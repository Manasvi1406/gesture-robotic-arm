from glob import glob
from setuptools import setup

package_name = "gesture_arm_ros2"

setup(
    name=package_name,
    version="1.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.py")),
        ("share/" + package_name + "/urdf", glob("urdf/*.urdf")),
        ("share/" + package_name + "/rviz", glob("rviz/*.rviz")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Project Maintainer",
    maintainer_email="maintainer@example.com",
    description="Hand-gesture controlled robotic arm simulation for ROS 2",
    license="MIT",
    entry_points={
        "console_scripts": [
            "gesture_node = gesture_arm_ros2.gesture_node:main",
        ],
    },
)
