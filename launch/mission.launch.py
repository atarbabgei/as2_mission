"""Run an AeroStack2 mission Python script against a running stack.

This does NOT launch the stack — bring that up first with as2_bringup.launch.py.
It simply executes a mission Python file (one that uses as2_python_api), passing
the namespace and sim-time flag the script expects.

Usage:
    # default bundled square mission:
    ros2 launch as2_mission mission.launch.py namespace:=drone0

    # point at any mission file:
    ros2 launch as2_mission mission.launch.py mission:=/path/to/my_mission.py namespace:=drone0
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration


def generate_launch_description() -> LaunchDescription:
    default_mission = os.path.join(
        get_package_share_directory('as2_mission'), 'missions', 'square_mission.py')

    namespace = LaunchConfiguration('namespace')
    mission = LaunchConfiguration('mission')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declared_args = [
        DeclareLaunchArgument(
            'namespace', default_value='drone0',
            description='Drone namespace (must match the bringup).'),
        DeclareLaunchArgument(
            'mission', default_value=default_mission,
            description='Path to the mission Python file to run.'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Pass -s (use simulation time) to the mission. true for SITL.'),
    ]

    # python3 <mission> -n <namespace> [-s]
    run_mission = ExecuteProcess(
        cmd=['python3', mission, '-n', namespace, '-s'],
        output='screen',
        condition=IfCondition(use_sim_time),
    )
    run_mission_no_sim = ExecuteProcess(
        cmd=['python3', mission, '-n', namespace],
        output='screen',
        condition=UnlessCondition(use_sim_time),
    )

    return LaunchDescription(declared_args + [run_mission, run_mission_no_sim])
