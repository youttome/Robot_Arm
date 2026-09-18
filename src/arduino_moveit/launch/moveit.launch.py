import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    
    is_sim_arg = DeclareLaunchArgument(
        name='is_sim',
        default_value='true'
    )

    is_sim = LaunchConfiguration('is_sim')

    arduino_model_share = get_package_share_directory('arduino_model')
    arduino_moveit_share = get_package_share_directory('arduino_moveit')

    moveit_config = (
        MoveItConfigsBuilder(
            'arduino_robot',
            package_name='arduino_moveit'
        )
        .robot_description(
            file_path=os.path.join(
                arduino_model_share,
                'urdf',
                'model_gazebo.urdf.xacro'
            )
        )
        .robot_description_semantic(
            file_path=os.path.join(
                arduino_moveit_share,
                'config',
                'arduino_move.srdf'
            )
        )
        .robot_description_kinematics(
            file_path=os.path.join(
                arduino_moveit_share,
                'config',
                'kinematics.yaml'
            )
        )
        .planning_pipelines(
            default_planning_pipeline='ompl',
            pipelines=['ompl'],
            load_all=False
        )
        .trajectory_execution(
            file_path=os.path.join(
                arduino_moveit_share,
                'config',
                'moveit_controllers.yaml'
            )
        )
        .to_moveit_configs()
    )

    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            moveit_config.to_dict(),
            {
                'use_sim_time': is_sim,
                'publish_robot_description_semantic': True
            }
        ],
        arguments=[
            '--ros-args',
            '--log-level',
            'info'
        ]
    )

    rviz_config = os.path.join(
        arduino_moveit_share,
        'config',
        'moveit.rviz'
    )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d',
            rviz_config
        ],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_kinematics,
            moveit_config.robot_description_semantic,
            moveit_config.joint_limits,
            {'use_sim_time': is_sim}
        ]
    )

    return LaunchDescription([
        is_sim_arg,
        move_group_node,
        rviz2_node
    ])
