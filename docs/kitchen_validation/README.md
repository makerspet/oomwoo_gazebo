# Polished kitchen validation evidence

Validation was run in Ubuntu 24.04 WSL 2 with ROS 2 Jazzy, `ros_gz_sim`,
`ros_gz_bridge`, and Gazebo Sim 8.11.0 (Harmonic line). The exact launch was:

```bash
source /opt/ros/jazzy/setup.bash
source /root/makerspet_ws/install/setup.bash
ros2 launch oomwoo_gazebo world.launch.py world:=kitchen.world \
  headless:=true robot_model:=oomwoo_one
```

`makerspet-kitchen-collision.log` records the real launch: `kitchen.world`
loaded, OOMWOO-One was created, Gazebo initialized diff drive, odometry, IMU,
lidar/range/ToF sensors, and the ROS/Gazebo bridge. A case-insensitive search
of that log found no missing-resource, URI, texture, mesh, or fatal-SDF error.
`makerspet-kitchen-no-manual-resource.log` repeats the launch with
`GZ_SIM_RESOURCE_PATH` unset; the package launch file supplied its installed
local `models/` path and the world still spawned without resource errors.

## GUI render evidence

`kitchen_gui_materials.png` is a real screenshot from Gazebo's `/gui/screenshot`
service during a WSLg GUI run. It visibly shows the local brown tile floor,
wood cabinetry/island surfaces, appliance details, and the robot/obstacles in
the room. The first GUI capture, `kitchen_gui_overview.png`, exposed overly
dark PBR surfaces; the materials were corrected with diffuse fallbacks and
non-metal PBR settings, rebuilt, and verified in the final screenshot.

## Motion evidence

The ROS bridge exposes `/cmd_vel`; a ROS `geometry_msgs/msg/Twist` forward
publish moved the simulated robot (Gazebo `/odom`) from approximately
`(-2.00, -0.50)` to `(-1.57, -0.50)`, and a subsequent zero command stopped
it. The direct Gazebo transport captures are retained because this headless WSL
run advances faster than wall time: a bounded direct `cmd_vel` pulse moved it
from `(-2.00, -0.50)` to `(-1.98, -0.50)`. A slow route then reached
`(-0.87, -0.50)`, turned, and reached `(0.76, -0.19)` via the south-side
island circulation. `kitchen-lidar-sample.txt` contains an actual 360-ray scan.

## Runtime collision observations

Four low-speed, direct Gazebo contact checks were completed after controlled
pose resets. `island-impact2-bumper-right.txt` identifies
`island_base::link::collision`; `counter-impact-bumper-right.txt` identifies
`north_counter_toekick::link::collision`; `fridge-impact-bumper-right.txt`
identifies `refrigerator::link::collision`; and
`dining-leg-bumper-right2.txt` identifies
`dining_table::link::leg3_collision`. In each case the robot stopped at the
expected boundary and did not pass through the static structure. These are
runtime observations, not inferred shape checks.

`toy-pose-before.txt` and `toy-pose-after.txt` show the dynamic toy ball move
from `(1.65, -1.45)` to approximately `(1.6504, -1.0109)` during a low-speed
robot approach. The selected pet-bowl approach did not publish a bumper contact
message, so no bowl-contact claim is made; the bowl remains a low lidar-visible
obstacle rather than a verified bumper obstacle.

The initial doorway check showed that the room slab ended at the threshold, so
`doorway_landing` was added and the package rebuilt. `doorway-landing-after.txt`
then records a controlled crossing from the kitchen at `y=-2.2` to the supported
landing at `y=-3.2398`; this is the final doorway result.

## Scope limits

This is a controlled drive/sensor smoke check, not an autonomous Nav2 claim.
No GUI screenshot is included because the validation was intentionally
headless. A forced bumper contact specifically against the pet bowl was not
observed; the collision design is audited in `../KITCHEN_WORLD_AUDIT.md` and
the bowl's runtime bumper outcome remains unverified.
