from click import Command

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
import os 
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command , LaunchConfiguration

def generate_launch_description():

    model_path = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(get_package_share_directory("arduino_model"),"urdf","model.urdf.xacro"),
        description="path of model xacro file to arduino robot"
        )
    
    robot_discription = ParameterValue(Command(["xacro ", LaunchConfiguration("model")]),value_type=str)

    robot_state_publisher=Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description':robot_discription}]
    )

    joint_state_publisher_gui=Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    rviz2=Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(get_package_share_directory("arduino_model"),"rviz","display.rviz") ]
    )


    return LaunchDescription([
        model_path,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz2
    ])
