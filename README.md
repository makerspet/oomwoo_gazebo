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
  system), plus `empty.world` and the TurtleBot3 worlds.
- `models/` — furniture and prop meshes used by the worlds.
- `map/` — saved maps aligned to the worlds.
- `launch/` — `world.launch.py` (spawn a world + robot), `self_drive_gazebo.launch.py`
  (simple wander behaviour).
- `src/`, `include/oomwoo_gazebo/` — the `self_drive_gazebo` C++ node.

## Usage
```
ros2 launch oomwoo_gazebo world.launch.py                 # with the Gazebo GUI
ros2 launch oomwoo_gazebo world.launch.py headless:=true  # no GUI (Docker / CI)
```
For the OOMWOO headless simulation and the coverage / navigation regressions, this
package is driven by the `oomwoo_sim_support` harness in
[oomwoo-ros2-tools](https://github.com/makerspet/oomwoo-ros2-tools) — see that repo
for the full sim workflow.

## Credits
Forked from [kaiaai/kaiaai_gazebo](https://github.com/kaiaai/kaiaai_gazebo)
(Apache-2.0). Initial versions are based on ROBOTIS
[TurtleBot3 simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations).

## License
[Apache License 2.0](LICENSE).
