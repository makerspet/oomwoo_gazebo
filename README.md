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
renamed to the **`oomwoo_gazebo`** package. The one functional change from upstream:
`living_room.world` loads the world-level `gz-sim-contact-system`, so the robot's
bumper/contact sensors actually publish — without it the contact topics exist but
stay permanently silent (see
[oomwoo-one/docs/sim-bumpers.md](https://github.com/makerspet/oomwoo-one/blob/main/docs/sim-bumpers.md)).

## Package contents
- `worlds/` — `living_room.world` (the cluttered test world, with the contact
  system), plus `empty.world` and the TurtleBot3 worlds. Also `kitchen.sdf`,
  `multi_room.sdf` and `narrow_passage.sdf`, contributed by
  [Alvaro Samudio](https://github.com/alvarosamudio/oomwoo_gazebo) — see
  [Contributed worlds](#contributed-worlds).
- `models/` — furniture and prop meshes used by the worlds.
- `map/` — saved maps aligned to the worlds.
- `launch/` — `world.launch.py` (spawn a world + robot), `self_drive_gazebo.launch.py`
  (simple wander behaviour).
- `src/`, `include/oomwoo_gazebo/` — the `self_drive_gazebo` C++ node.

## Usage
```
ros2 launch oomwoo_gazebo world.launch.py                 # with the Gazebo GUI
ros2 launch oomwoo_gazebo world.launch.py headless:=true  # no GUI (Docker / CI)
ros2 launch oomwoo_gazebo world.launch.py world:=kitchen.sdf   # pick a world
```
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

The geometry is unmodified from the contributed originals. Two things were
changed, both to match the other worlds in this package:

- **World plugins.** The originals load `gz-sim-cpu-lidar-system`, which Gazebo
  Harmonic (ROS 2 Jazzy) does not ship, so `/scan` would stay silent; they also
  omitted `gz-sim-imu-system`. Both fixed.
- **Physics.** The originals declared `dart` with the `bullet` collision
  detector; these now carry the same `ode` block as the `.world` files.

```
ros2 launch oomwoo_gazebo world.launch.py world:=multi_room.sdf
ros2 launch oomwoo_gazebo world.launch.py world:=narrow_passage.sdf
```

These have no maps in `map/`, so run them with SLAM rather than localization
against a saved map.

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
