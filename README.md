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
| `software_gl` | `false` | `true` `false` | Force Mesa software GL for the GUI — see [Software GL](#software-gl) |
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

#### Software GL
Use `software_gl:=true` if the Gazebo **GUI** dies on startup with:

```
[GUI] [Err] [Ogre2RenderEngine.cc] OGRE EXCEPTION(2:InvalidParametersException):
      Option named Full Screen does not exist. in EglPBufferSupport::setConfigOption
[GUI] [Err] [BaseRenderEngine.cc] Render-engine has not been initialized
```

The `ogre2` render engine needs OpenGL 3.3+. When it cannot get that from the X
server it falls back to an EGL PBuffer context, which has no `Full Screen`
option, and the GUI never initializes. This is typical of **Docker on Windows or
macOS driving an external X server** (`DISPLAY=host.docker.internal:0.0`) with no
GPU passed through — there is no `--gpus` flag and no `/dev/dri`. It tends to be
*intermittent*, because it depends on what the X server negotiates on that run.

`software_gl:=true` sets `LIBGL_ALWAYS_SOFTWARE=1` and `GALLIUM_DRIVER=llvmpipe`,
so Mesa's software rasteriser supplies OpenGL 4.5 inside the container and
`ogre2` keeps its normal windowed path. Rendering is slower, but it no longer
depends on the X server's GL at all. `headless:=true` already implies this.

```
ros2 launch oomwoo_gazebo world.launch.py world:=kitchen_dining.world software_gl:=true
```

The alternative is to give the container a real GPU (`--gpus all` plus
`/dev/dri`), which keeps hardware rendering.

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

They are self-contained: every model is inline `box` and `plane` geometry with
inline colour materials — no `<include>`, `<uri>` or `<mesh>` anywhere, so unlike
the `.world` files (`living_room.world` alone pulls in 26 models) they need
nothing from `models/` and download nothing at run time. Each is about 6 KB.

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

`kitchen.sdf` and `multi_room.sdf` are geometrically unmodified.

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

## Model attribution

Every third-party model in `models/` is vendored locally so worlds load with no
run-time downloads. Most are **CC BY 4.0**, which requires attribution — this is
that attribution. Each model also keeps its own upstream `model.config` with the
authors and licence text intact.

**How the original author was determined.** Fuel does not prevent anyone from
downloading someone else's model and re-uploading it under their own account, and
several models here have exactly that (see [Re-uploads](#re-uploads) below). Two
signals were used together:

1. the `<author>` block inside the model's own `model.config` — re-uploaders
   generally carry it over unedited, so it survives the copy;
2. the **earliest** `upload_date` across every Fuel model sharing that name.

Where the two disagree, the embedded author wins. `cardboard_box` is the case in
point: `german` posted it on 2018-01-02, 25 days *before* the OpenRobotics
account did, but both uploads have byte-identical meshes and both `model.config`
files credit Nate Koenig and Cole Biesemeyer. So it is an Open Robotics model
that a third party happened to publish to Fuel first, and it is credited that way
below.

| Model | Author(s) | Published by | Licence | First on Fuel |
|---|---|---|---|---|
| `Bookshelf` | Nate Koenig | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Bookshelf) | CC0 1.0 | 2018-01-27 |
| `Cabinet` | Nate Koenig | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Cabinet) | CC0 1.0 | 2018-01-27 |
| `cardboard_box` | Nate Koenig, Cole Biesemeyer | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Cardboard%20Box) | CC BY 4.0 | 2018-01-02 (by `german`, see above) |
| `Chair` | Cole Biesemeyer | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Chair) | CC BY 4.0 | 2020-05-20 |
| `coffee_maker` | Cole Biesemeyer, Louise Poubel | [chapulina](https://app.gazebosim.org/chapulina/fuel/models/Coffee%20Maker) | CC BY 4.0 | 2018-05-29 |
| `CoffeeTable` | Open Robotics | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/CoffeeTable) | CC BY 4.0 | 2020-08-06 |
| `DiningChair` | Cole Biesemeyer, L_Krajewski | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Dining%20Chair) | CC BY 4.0 | 2023-09-29 |
| `DiningTable` | Cole Biesemeyer, MechanicalOnion | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Dining%20Table) | CC BY 4.0 | 2023-09-29 |
| `FemaleVisitorSit` | Wan Yi Seow | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/FemaleVisitorSit) | CC BY 4.0 | 2020-05-20 |
| `ground plane` | Nate Koenig | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Ground%20Plane) | CC0 1.0 | 2018-01-27 |
| `LampAndStand` | Roselle Carmen | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/LampAndStand) | CC BY 4.0 | 2020-05-20 |
| `MaleVisitorSit` | Wan Yi Seow | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/MaleVisitorSit) | CC BY 4.0 | 2020-05-20 |
| `MiniSofa` | Wan Yi | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/MiniSofa) | CC BY 4.0 | 2020-05-20 |
| `Oven` | Cole Biesemeyer, Francesco Coldesina | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Oven) | CC BY 4.0 | 2023-09-29 |
| `racoon` | Google | [GoogleResearch](https://app.gazebosim.org/GoogleResearch/fuel/models/Racoon) | CC BY 4.0 | 2020-09-18 |
| `Sofa` | Wan Yi Seow | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Sofa) | CC BY 4.0 | 2020-08-06 |
| `squirrel` | Google | [GoogleResearch](https://app.gazebosim.org/GoogleResearch/fuel/models/Squirrel) | CC BY 4.0 | 2020-09-18 |
| `sun` | Nate Koenig | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Sun) | CC0 1.0 | 2018-01-27 |
| `TableMarble` | Ian Chen | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/Table%20Marble) | CC0 1.0 | 2018-01-27 |
| `TVStand` | Roselle | [OpenRobotics](https://app.gazebosim.org/OpenRobotics/fuel/models/TVStand) | CC BY 4.0 | 2020-08-06 |

Not on Fuel under that name:

| Model | Author(s) | Source | Licence |
|---|---|---|---|
| `cat_figurines` | Google | [Google Scanned Objects](https://app.gazebosim.org/GoogleResearch/fuel/collections/Google%20Scanned%20Objects) | CC BY 4.0 |
| `turtlebot3_house`, `turtlebot3_world` | Taehun Lim (Darby) | ROBOTIS [turtlebot3_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations) | Apache-2.0 |

### Re-uploads

Same model, published to Fuel more than once under different accounts. Credit
belongs to the author in the left column, not to whoever uploaded a copy:

| Model | Credited to | Also uploaded by | Evidence |
|---|---|---|---|
| `Chair` | OpenRobotics, 2020-05-20 | Peyman1372, 2023-10-15 | identical file size (2677 KB) |
| `Sofa` | OpenRobotics, 2020-08-06 | sebbyjp, 2024-02-27 | identical file size (1280 KB) |
| `CoffeeTable` | OpenRobotics, 2020-08-06 | will0993, 2024-08-15 | same name, different size |
| `cardboard_box` | Open Robotics (Nate Koenig, Cole Biesemeyer) | `german` 2018-01-02, NGD1004 2023-03-02, jliu6718 2023-10-27 | `german`'s mesh is byte-identical to OpenRobotics' and carries the same authors in `model.config` |

Beyond the models this package uses, the same pattern shows up across Fuel —
`OfficeChairGrey` and `foldable_chair`, for instance, each exist twice at
identical byte sizes. Worth checking before crediting anything found there.

### Authored for this package

Original models, Apache-2.0 with the rest of this repo. By Ilia O.:
`door_08x2m`, `kaiaai_poster`, `makerspet_poster`, `pet_gate`, `pet_gate_wide`,
`red_ball_10in`, `room_wall_2x5m`, `rug_ivory_2m`, `tv_65in_emissive`,
`window_curtains`.

The kitchen family — `kitchen_base_run_w`/`_e`/`_east`, `kitchen_wall_cab_w`/
`_e`/`_ec`/`_es`, `kitchen_pantry`, `fridge_double_door`, `dishwasher`,
`range_hood`, `room_wall_25x4m`, `room_wall_25x5m`, `window_curtains_small` —
was authored for `kitchen_dining.world`, because Fuel has no residential-height
counter, no toe kick on anything, and no range hood at all. Their door and
counter textures are reused from `Cabinet` (`wood.png`) and `TableMarble`
(`marble.png`), both CC0 1.0, so those carry no attribution requirement.

## License
[Apache License 2.0](LICENSE).
