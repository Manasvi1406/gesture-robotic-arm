import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory("gesture_arm_ros2")
    with open(os.path.join(share, "urdf", "gesture_arm.urdf")) as f:
        robot_description = f.read()

    args = [
        DeclareLaunchArgument("demo", default_value="false",
                              description="Synthetic motion, no camera"),
        DeclareLaunchArgument("camera_index", default_value="0"),
        DeclareLaunchArgument("rate_hz", default_value="30.0"),
        DeclareLaunchArgument("show_preview", default_value="true"),
        DeclareLaunchArgument("udp_input", default_value="false",
                              description="Receive gesture JSON from external UDP sender"),
        DeclareLaunchArgument("udp_input_host", default_value="0.0.0.0"),
        DeclareLaunchArgument("udp_input_port", default_value="5005"),
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("udp_enabled", default_value="false",
                              description="Also stream joints to Unity over UDP"),
        DeclareLaunchArgument("udp_port", default_value="5005"),
    ]

    return LaunchDescription(args + [
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[{"robot_description": robot_description}]),
        Node(package="gesture_arm_ros2", executable="gesture_node", output="screen",
             parameters=[{
                 "demo": ParameterValue(LaunchConfiguration("demo"), value_type=bool),
                 "camera_index": ParameterValue(LaunchConfiguration("camera_index"), value_type=int),
                 "rate_hz": ParameterValue(LaunchConfiguration("rate_hz"), value_type=float),
                 "show_preview": ParameterValue(LaunchConfiguration("show_preview"), value_type=bool),
                 "udp_input": ParameterValue(LaunchConfiguration("udp_input"), value_type=bool),
                 "udp_input_host": LaunchConfiguration("udp_input_host"),
                 "udp_input_port": ParameterValue(LaunchConfiguration("udp_input_port"), value_type=int),
                 "udp_enabled": ParameterValue(LaunchConfiguration("udp_enabled"), value_type=bool),
                 "udp_port": ParameterValue(LaunchConfiguration("udp_port"), value_type=int),
             }]),
        Node(package="rviz2", executable="rviz2",
             arguments=["-d", os.path.join(share, "rviz", "gesture_arm.rviz")],
             condition=IfCondition(LaunchConfiguration("rviz"))),
    ])
