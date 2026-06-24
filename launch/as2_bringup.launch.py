"""Bring up the AeroStack2 stack for a PX4/Pixhawk drone (platform first, then the rest).

Usage:
    ros2 launch as2_mission as2_bringup.launch.py namespace:=drone0 controller:=pid
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def _include(pkg: str, launch_file: str, launch_arguments: dict):
    """Include another package's launch file with the given arguments."""
    path = PathJoinSubstitution([FindPackageShare(pkg), 'launch', launch_file])
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(path),
        launch_arguments=launch_arguments.items(),
    )


def generate_launch_description() -> LaunchDescription:
    config_dir = os.path.join(get_package_share_directory('as2_mission'), 'config')

    namespace = LaunchConfiguration('namespace')
    controller = LaunchConfiguration('controller')
    config_file = LaunchConfiguration('config_file')
    startup_delay = LaunchConfiguration('startup_delay')

    declared_args = [
        DeclareLaunchArgument(
            'namespace', default_value='drone0',
            description='Drone namespace (must match the mission and PX4 setup).'),
        DeclareLaunchArgument(
            'controller', default_value='pid_speed_controller',
            description='Motion controller plugin: pid_speed_controller or '
                        'differential_flatness_controller.'),
        DeclareLaunchArgument(
            'config_file', default_value=os.path.join(config_dir, 'config.yaml'),
            description='Shared AeroStack2 config (platform, estimator, behaviors).'),
        DeclareLaunchArgument(
            'startup_delay', default_value='4.0',
            description='Seconds to wait after the platform before starting the '
                        'estimator/controller/behaviors so the handshake succeeds.'),
    ]

    # The controller plugin config lives next to config.yaml, named <plugin>.yaml.
    # Build the path as a concatenation substitution: "<config_dir>/<plugin>.yaml".
    plugin_config_file = [os.path.join(config_dir, ''), controller, '.yaml']

    # 1) Platform FIRST (talks to PX4 over uXRCE-DDS).
    platform = _include(
        'as2_platform_pixhawk', 'pixhawk_launch.py',
        {'namespace': namespace, 'platform_config_file': config_file})

    # 2..4) Estimator, controller, behaviors — after the platform is up.
    estimator = _include(
        'as2_state_estimator', 'state_estimator_launch.py',
        {'namespace': namespace, 'config_file': config_file})

    motion_controller = _include(
        'as2_motion_controller', 'controller_launch.py',
        {'namespace': namespace,
         'config_file': config_file,
         'plugin_name': controller,
         'plugin_config_file': plugin_config_file})

    behaviors = _include(
        'as2_behaviors_motion', 'motion_behaviors_launch.py',
        {'namespace': namespace, 'config_file': config_file})

    delayed_stack = TimerAction(
        period=startup_delay,
        actions=[estimator, motion_controller, behaviors],
    )

    return LaunchDescription(declared_args + [platform, delayed_stack])
