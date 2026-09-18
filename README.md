# Robot Arm

A ROS 2 robot arm simulation project using **Gazebo, RViz, MoveIt 2, and ros2_control**.

The project provides a simulated environment that represents the behavior and control of a real robot arm. It can be used for development and testing before connecting the system to real hardware.

The project can also be extended with **AI models**, sensors, computer vision, or integrated into a larger robotics project.

It was developed to work with **ROS 2 Lyrical**.

### Required ROS 2 Packages

```bash
sudo apt install \
    ros-lyrical-rviz2 \
    ros-lyrical-controller-manager \
    ros-lyrical-robot-state-publisher \
    ros-lyrical-ros-gz-sim \
    ros-lyrical-ros-gz-bridge \
    ros-lyrical-moveit-ros-move-group \
    ros-lyrical-moveit-planners-ompl
```

> `gazebo11` and `libgazebo11-dev` are Gazebo Classic packages. This project uses **Gazebo Sim** through `ros-lyrical-ros-gz-sim`.

For MoveIt 2 installation and setup:

https://moveit.picknik.ai/main/doc/tutorials/getting_started/getting_started.html#create-a-colcon-workspace-and-download-tutorials


## Run

Clone the repository and build the workspace:

```bash
git clone https://github.com/youttome/Robot_Arm.git
cd Robot_Arm

source /opt/ros/lyrical/setup.bash
colcon build
source install/setup.bash
```

### Recommended: Automatic Startup

The recommended way to run the project is:

```bash
./start_robot_arm.sh
```

The script starts Gazebo, starts the controllers, checks that they are active, and then starts MoveIt and RViz.

### Manual Startup

#### 1. Start Gazebo

```bash
ros2 launch arduino_model display.gazebo.launch.py
```

#### 2. Start Controllers

```bash
ros2 launch arduino_controller control.launch.py
```

After the controller manager starts, check that all controllers are active:

```bash
ros2 control list_controllers
```

Expected output:

```text
joint_state_broadcaster   joint_state_broadcaster/JointStateBroadcaster          active
gripper_control            joint_trajectory_controller/JointTrajectoryController  active
arm_control                joint_trajectory_controller/JointTrajectoryController  active
```


#### 3. Start MoveIt and RViz

```bash
ros2 launch arduino_moveit moveit.launch.py
```

When RViz opens, load the provided:

```text
src/arduino_moveit/config/moveit.rviz
```

from the RViz configuration/settings menu.


