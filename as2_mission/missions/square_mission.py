#!/usr/bin/env python3
"""Simple single-drone square mission using the AeroStack2 Python API.

Sequence: arm -> offboard -> takeoff -> fly a square -> land.
Run it either directly, via the mission launch file, or with `ros2 run`:

    python3 square_mission.py -n drone0 -s
    ros2 launch as2_mission mission.launch.py namespace:=drone0
    ros2 run as2_mission square_mission -n drone0 -s
"""

import argparse
from time import sleep

from as2_python_api.drone_interface import DroneInterface
import rclpy

TAKE_OFF_HEIGHT = 1.0   # m
TAKE_OFF_SPEED = 0.5    # m/s
SLEEP_TIME = 0.5        # s between behaviors
SPEED = 1.0             # m/s
HEIGHT = 1.0            # m
SIDE = 2.0              # half-side of the square (m)
LAND_SPEED = 0.5        # m/s

PATH = [
    [-SIDE, SIDE, HEIGHT],
    [-SIDE, -SIDE, HEIGHT],
    [SIDE, -SIDE, HEIGHT],
    [SIDE, SIDE, HEIGHT],
]


def drone_start(drone: DroneInterface) -> bool:
    """Arm, switch to offboard and take off."""
    print('Start mission')
    print('Arm:', drone.arm())
    print('Offboard:', drone.offboard())
    success = drone.takeoff(height=TAKE_OFF_HEIGHT, speed=TAKE_OFF_SPEED)
    print('Take Off:', success)
    return success


def drone_run(drone: DroneInterface) -> bool:
    """Fly the square, keep-yaw then path-facing."""
    print('Run mission')
    for goal in PATH:
        print(f'Go to (keep yaw) {goal}')
        if not drone.go_to.go_to_point(goal, speed=SPEED):
            return False
        sleep(SLEEP_TIME)
    for goal in PATH:
        print(f'Go to (path facing) {goal}')
        if not drone.go_to.go_to_point_path_facing(goal, speed=SPEED):
            return False
        sleep(SLEEP_TIME)
    return True


def drone_end(drone: DroneInterface) -> bool:
    """Land. (manual() is intentionally omitted: the Pixhawk platform rejects
    switching to MANUAL from the companion computer, which only logs a harmless
    error. The drone auto-disarms after landing.)"""
    print('End mission')
    success = drone.land(speed=LAND_SPEED)
    print('Land:', success)
    return success


def main():
    parser = argparse.ArgumentParser(description='Single drone square mission')
    parser.add_argument('-n', '--namespace', type=str, default='drone0',
                        help='Drone namespace')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Enable verbose output')
    parser.add_argument('-s', '--use_sim_time', action='store_true', default=False,
                        help='Use simulation time (SITL)')
    args = parser.parse_args()

    print(f'Running square mission for drone {args.namespace}')
    rclpy.init()
    uav = DroneInterface(
        drone_id=args.namespace,
        use_sim_time=args.use_sim_time,
        verbose=args.verbose)

    if drone_start(uav):
        drone_run(uav)
    drone_end(uav)

    uav.shutdown()
    rclpy.shutdown()
    print('Clean exit')


if __name__ == '__main__':
    main()
