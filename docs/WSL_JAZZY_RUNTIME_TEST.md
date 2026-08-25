# WSL Jazzy / Gazebo Harmonic runtime check

This package was built and exercised on 2026-08-24 in a fresh `Ubuntu-24.04`
WSL 2 distribution.  ROS 2 Jazzy is packaged for Ubuntu 24.04; the existing
Ubuntu 26.04 WSL distribution was therefore not used for the binary runtime.

## Installed runtime

```bash
sudo apt-get install -y \
  ros-jazzy-ros-base \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  python3-rosdep \
  python3-colcon-common-extensions \
  build-essential
```

`gz sim --versions` reported `8.11.0`, the Gazebo Harmonic release line.

## Workspace build

The package was built with its runtime robot dependencies checked out on their
`jazzy` branches: `kaiaai_msgs`, `kaiaai`, and `oomwoo-one`.

```bash
source /opt/ros/jazzy/setup.bash
cd /root/makerspet_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Headless kitchen test

```bash
export GZ_SIM_RESOURCE_PATH="$PWD/install/oomwoo_gazebo/share/oomwoo_gazebo/models:${GZ_SIM_RESOURCE_PATH:-}"
timeout --signal=INT 45s ros2 launch oomwoo_gazebo world.launch.py \
  world:=kitchen.sdf headless:=true robot_model:=oomwoo_one
```

Observed success signals before the intentionally bounded shutdown:

- Gazebo Sim 8.11.0 loaded `worlds/kitchen.sdf` and initialized world `kitchen`.
- `ros_gz_sim` reported `Entity creation successful` for `oomwoo_one`.
- The Gazebo server created the robot entity and enabled diff-drive, odometry,
  joint-state, contact, IMU, lidar, range, and point-cloud sensor systems.
- `ros_gz_bridge` started bridges for `/clock`, odometry, TF, scan, IMU, ranges,
  cameras, and `cmd_vel`.

The `SIGINT` exit caused by the 45-second `timeout --signal=INT` is expected:
it is an intentionally bounded test shutdown, not a simulation startup
failure.

## Final polished kitchen.world validation

The earlier test above exercised the upstream `kitchen.sdf`; it is not evidence
for the polished world. The final world was rebuilt from this branch and run as:

```bash
source /opt/ros/jazzy/setup.bash
cd /root/makerspet_ws
colcon build --symlink-install --packages-select oomwoo_gazebo
source install/setup.bash
timeout --signal=INT 120s ros2 launch oomwoo_gazebo world.launch.py \
  world:=kitchen.world headless:=true robot_model:=oomwoo_one
```

The actual log records successful `kitchen.world` loading, OOMWOO-One spawning,
bridge creation, IMU and lidar initialization, and diff-drive/odometry setup.
See `docs/kitchen_validation/` for captured launch, odometry, and lidar
evidence. `world.launch.py` sets `GZ_SIM_RESOURCE_PATH` to the installed local
`models/` directory, so the vendored maps resolve without a manual environment
export or a Fuel download. The run is headless; no GUI screenshot was fabricated.
