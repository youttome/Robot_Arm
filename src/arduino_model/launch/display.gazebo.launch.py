from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory

import os

from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    IncludeLaunchDescription
)

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from pathlib import Path


def generate_launch_description():

    # ============================================================
    # Package path
    # ============================================================

    package_path = get_package_share_directory("arduino_model")


    # ============================================================
    # Robot model
    # ============================================================

    model_file_path = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(
            package_path,
            "urdf",
            "model_gazebo.urdf.xacro"
        ),
        description="Path to robot model"
    )

    robot_description = ParameterValue(
        Command([
            "xacro ",
            LaunchConfiguration("model")
        ]),
        value_type=str
    )


    # ============================================================
    # Robot State Publisher
    # ============================================================

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True
            }
        ]
    )


    # ============================================================
    # Gazebo resource path
    # Allows Gazebo to find meshes / models inside workspace
    # ============================================================

    gazebo_source_env = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[
            str(Path(package_path).parent.resolve())
        ]
    )


    # ============================================================
    # Gazebo
    # ============================================================

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            "gz_args": "-v 4 -r empty.sdf"
        }.items()
    )


    # ============================================================
    # Spawn robot into Gazebo
    # ============================================================

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "robot_description",
            "-name",
            "arduinorobot"
        ],
        output="screen"
    )


    # ============================================================
    # Gazebo <-> ROS 2 bridge
    # ============================================================

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"
        ],
        output="screen"
    )


    # ============================================================
    # Launch description
    # ============================================================

    return LaunchDescription([
        model_file_path,
        robot_state_publisher,
        gazebo_source_env,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge
    ])