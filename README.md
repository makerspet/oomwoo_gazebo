<div align="center">

# OOMWOO Gazebo

*Open-source robot vacuum you build yourself.*

ROS 2 Jazzy · Gazebo · Worlds · Models · Contact sensors · Simulation

![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)
[![Part of OOMWOO](https://img.shields.io/badge/part%20of-OOMWOO-5eead4)](https://github.com/makerspet/oomwoo)

</div>

Gazebo worlds and models for the [OOMWOO](https://github.com/makerspet/oomwoo)
open-source robot vacuum simulation.

A fork of [kaiaai/kaiaai_gazebo](https://github.com/kaiaai/kaiaai_gazebo) (jazzy),
renamed to the **`oomwoo_gazebo`** package. Functional changes from upstream:

- `living_room.world` loads the world-level `gz-sim-contact-system`, so the
  robot's bumper/contact sensors actually publish — without it the contact
  topics exist but stay permanently silent (see
  [oomwoo-one/docs/sim-bumpers.md](https://github.com/makerspet/oomwoo-one/blob/main/docs/sim-bumpers.md)).
- `world.launch.py` gained a `headless` mode for Docker/CI, an `odom_source`
  switch for ground-truth vs wheel odometry, and per-sensor `enable_*` switches
  to trade sensor coverage for simulation speed. See
  [`world.launch.py` arguments](#worldlaunchpy-arguments).
- Three extra worlds, see [Contributed worlds](#contributed-worlds).

## Package contents
- `worlds/` — `living_room.world` (the cluttered test world, with the contact
  system), plus `empty.world` and the TurtleBot3 worlds. Also `kitchen.sdf`,
  `multi_room.sdf` and `narrow_passage.sdf`, contributed by
  [Alvaro Samudio](https://github.com/alvarosamudio/oomwoo_gazebo) — see
  [Contributed worlds](#contributed-worlds).
- `models/` — furniture and prop meshes used by the worlds.
- `map/` — saved maps aligned to the worlds.
- `launch/` — `world.launch.py` (spawn a world + robot; see
  [arguments](#worldlaunchpy-arguments)), `self_drive_gazebo.launch.py`
  (simple wander behaviour).
- `src/`, `include/oomwoo_gazebo/` — the `self_drive_gazebo` C++ node.

## Usage
```
ros2 launch oomwoo_gazebo world.launch.py                       # GUI, living_room.world
ros2 launch oomwoo_gazebo world.launch.py headless:=true        # no GUI (Docker / CI)
ros2 launch oomwoo_gazebo world.launch.py world:=kitchen.sdf    # pick a world
```
`world.launch.py` starts Gazebo, bridges it to ROS 2, publishes the robot
description and spawns the robot.

### `world.launch.py` arguments

| Argument | Default | Values | Purpose |
|---|---|---|---|
| `world` | `living_room.world` | any file in `worlds/` | World to load, resolved from this package's `worlds/` |
| `robot_model` | *(from config)* | package name | Robot description package. Empty means read `robot.model` from the kaiaai config (`~/.kaiaai.yaml`) |
| `use_sim_time` | `true` | `true` `false` | Use the Gazebo clock |
| `headless` | `false` | `true` `false` | No GUI — see [Headless](#headless) |
| `x_pose` | `-2.0` | float | Robot spawn X |
| `y_pose` | `-0.5` | float | Robot spawn Y |
| `odom_source` | `truth` | `truth` `wheel` | Which odometry owns `/odom` + `/tf` — see [Odometry source](#odometry-source) |
| `enable_lidar` | `true` | `true` `false` | 2D LiDAR `/scan` |
| `enable_ranges` | `true` | `true` `false` | Side distance sensors `/range_left`, `/range_right` |
| `enable_tof` | `true` | `true` `false` | Front ToF `/tof_front/points` |
| `enable_cameras` | `false` | `true` `false` | Stereo `/camera_left`, `/camera_right` — **off by default** (heavy, unused for now) |
| `enable_imu` | `true` | `true` `false` | IMU `/imu` |

#### Headless
`headless:=true` runs Gazebo server-only with offscreen rendering and forces
software GL (`LIBGL_ALWAYS_SOFTWARE=1`, `GALLIUM_DRIVER=llvmpipe`), so the
rendering sensors still produce data with no display attached. This is the mode
for Docker and CI.

#### Odometry source
`odom_source` selects which odometry owns `/odom` and `/tf`:

- `truth` — ground-truth model pose, slip-free.
- `wheel` — wheel-encoder odometry, drifts with wheel slip.

Both are always published: whichever is *not* selected appears on `/odom_truth`
or `/odom_wheel`, so the two can be compared to measure slip.

#### Sensor switches
The `enable_*` arguments are passed into the robot's xacro, so the sensor links
stay in the model and only the Gazebo sensor — the render cost — is dropped.
Turn them off to speed up the simulation. Cameras and the front ToF cost the
most, then the side ranges, then the LiDAR; cameras are already off by default.

```
ros2 launch oomwoo_gazebo world.launch.py headless:=true \
  enable_tof:=false enable_ranges:=false
```

These require matching `xacro:arg` declarations in the robot description
package, as in `oomwoo_one`'s `urdf/plugins.xacro`.

For the OOMWOO headless simulation and the coverage / navigation regressions, this
package is driven by the `oomwoo_sim_support` harness in
[oomwoo-ros2-tools](https://github.com/makerspet/oomwoo-ros2-tools) — see that repo
for the full sim workflow.

## Contributed worlds
`kitchen.sdf`, `multi_room.sdf` and `narrow_passage.sdf` were contributed by
[Alvaro Samudio](https://github.com/alvarosamudio) and vendored here from
[alvarosamudio/oomwoo_gazebo](https://github.com/alvarosamudio/oomwoo_gazebo)
(Apache-2.0), which hosts an independent OOMWOO simulation stack. Only the
worlds are vendored — that repo declares a package also named `oomwoo_gazebo`,
so the two cannot be built in one colcon workspace.

`multi_room.sdf` and `narrow_passage.sdf` remain self-contained with inline
primitive geometry. `kitchen.sdf` now reuses the package-local `model://Chair`
asset for realistic furniture instead of placeholder chair boxes. It still
requires no network download at run time as long as this package's `models/`
directory is available.

Two things were changed in all three, to match the other worlds in this package:

- **World plugins.** The originals load `gz-sim-cpu-lidar-system`, which Gazebo
  Harmonic (ROS 2 Jazzy) does not ship, so `/scan` would stay silent; they also
  omitted `gz-sim-imu-system`. Both fixed.
- **Physics.** The originals declared `dart` with the `bullet` collision
  detector; these now carry the same `ode` block as the `.world` files.

`narrow_passage.sdf` needed two geometry fixes as well, both sized against the
robot's 0.349 m body (0.359 m including the bumper):

- Its corridor ran `x [-3.0, 3.0]`, which put the default spawn (`x_pose`
  `-2.0`, `y_pose` `-0.5`) *inside* the right corridor wall. The corridor now
  runs `x [-1.0, 3.0]`, so the robot spawns on open floor and drives into the
  passage. Keep the near end at `x >= -1.0` if you edit it.
- `box_obstacle` sat mid-corridor leaving 0.30 m to each wall, so the passage
  was impassable on both sides and the corridor was a dead end. It now sits
  flush against the right wall, leaving a single 0.60 m gap (0.12 m either side
  of the robot). Keep the clear gap above ~0.40 m.

`multi_room.sdf` remains geometrically unmodified. `kitchen.sdf` received a
manual dimensional cleanup: its 1.5 m partition-like walls are now 2.4 m high
and its placeholder box chairs use the existing Chair model. See
[`docs/kitchen-scale-audit.md`](docs/kitchen-scale-audit.md). A Gazebo GUI
visual pass is still required before calling the world visually validated.

```
ros2 launch oomwoo_gazebo world.launch.py world:=multi_room.sdf
ros2 launch oomwoo_gazebo world.launch.py world:=narrow_passage.sdf
```

These have no maps in `map/`, so run them with SLAM rather than localization
against a saved map.

## Release Notes

### 8/16/2026

- recreated `maps/living_room.*` map, including slam_toolbox graph pose data export

### 8/15/2026

- vendored `worlds/*.sdf`

## Credits
Forked from [kaiaai/kaiaai_gazebo](https://github.com/kaiaai/kaiaai_gazebo)
(Apache-2.0). Initial versions are based on ROBOTIS
[TurtleBot3 simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations).

The `kitchen`, `multi_room` and `narrow_passage` worlds are by
[Alvaro Samudio](https://github.com/alvarosamudio), from
[alvarosamudio/oomwoo_gazebo](https://github.com/alvarosamudio/oomwoo_gazebo)
(Apache-2.0).

## License
[Apache License 2.0](LICENSE).
