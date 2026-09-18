import os

from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node



def generate_launch_description():


    # =========================
    # ros2_control controllers
    # =========================

    controller_config = os.path.join(
        get_package_share_directory("arduino_controller"),
        "config",
        "arduino_Control.yaml"
    )

    print("controller_config:", controller_config)

    arm_controller_spawn = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "arm_control",
            "--controller-manager",
            "/controller_manager",
            "--param-file",
            controller_config
        ],
        output="screen"
    )

    gripper_controller_spawn = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "gripper_control",
            "--controller-manager",
            "/controller_manager",
            "--param-file",
            controller_config
        ],
        output="screen"
    )
    joint_state_broadcaster_spawn = Node(
            package="controller_manager",
            executable="spawner",
            arguments=[
                "joint_state_broadcaster",
                "--controller-manager",
                "/controller_manager"
            ]
    )
    return LaunchDescription([
        arm_controller_spawn,
        gripper_controller_spawn,
        joint_state_broadcaster_spawn
    ])