# as2_mission

Bring-up and mission orchestration for an AeroStack2 PX4/Pixhawk drone (PX4 **v1.16**).

One launch starts the whole AeroStack2 stack in the correct order; a second launch
runs a Python mission against it.

```bash
# 1. bring up the stack (platform → estimator → controller → behaviors)
ros2 launch as2_mission as2_bringup.launch.py namespace:=drone0
# 2. run a mission (defaults to the bundled square; or mission:=/path/to/your.py)
ros2 launch as2_mission mission.launch.py namespace:=drone0
```

## Dependencies (the patched stack this assumes)
This package needs an AeroStack2 + Pixhawk stack ported to **px4_msgs 1.16**. The
forks below pin a validated commit; the pid build fix is already committed in the
aerostack2 fork, so no manual patching is needed.

1. **aerostack2** fork `atarbabgei/aerostack2` — pinned at upstream `d3bcf5f9` plus the
   pid build fix (drops `find_package(pid_controller)`, which collides with
   ros2_controllers' unrelated `pid_controller`; always vendors RPS98/pid_controller).
   `git fetch upstream` pulls future upstream changes.
   *(Standalone alternative: upstream aerostack2 + `git apply patches/aerostack2-pid-controller-vendoring.patch`.)*

2. **as2_platform_pixhawk** fork `atarbabgei/as2_platform_pixhawk` — the v1.16 port.
   Renamed px4_msgs fields: `SensorGps` (`latitude_deg`/`longitude_deg`/`altitude_ellipsoid_m`,
   no 1e7/1e3 scaling), `VehicleAttitudeSetpoint` (no `*_body`, use `q_d`),
   `BatteryStatus.design_capacity` → NAN.

3. **px4_msgs** branch `release/1.16` (must match the PX4 v1.16 firmware).

4. **Micro-XRCE-DDS-Agent** (SITL: UDP `:8888`; real Pixhawk: serial).

## Get the whole stack
AeroStack2 keeps platform drivers (pixhawk, dji, crazyflie...) in separate repos, so
clone the four pieces into one workspace's `src/`:
```bash
mkdir -p ~/as2_ws/src && cd ~/as2_ws/src
git clone https://github.com/atarbabgei/aerostack2.git
git clone https://github.com/atarbabgei/as2_platform_pixhawk.git
git clone https://github.com/atarbabgei/as2_mission.git
git clone -b release/1.16 https://github.com/PX4/px4_msgs.git
cd ~/as2_ws && source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to as2_mission   # skips Gazebo/sim packages
```
`px4_msgs` (branch `release/1.16`) must match the PX4 v1.16 firmware — don't skip it.
(An `as2_px4.repos` manifest is also included if you prefer `vcs import`.)

## Config
`config/config.yaml` — `fmu_prefix: ""` (single-drone, PX4 publishes global `/fmu/...`).
For real outdoor flight enable the GPS estimator path; indoor needs external odom (VIO/mocap).
