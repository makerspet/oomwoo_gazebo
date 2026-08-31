# Kitchen world scale audit

This pass focuses on obvious dimensional / presentation errors that can be checked directly from the SDF without claiming a Gazebo GUI run.

## Robot reference

The package README documents the OOMWOO body as approximately **0.349 m**, or **0.359 m including the bumper**. That is the reference used for navigation clearances.

## Findings

| Element | Previous geometry | Finding | Action |
|---|---:|---|---|
| Room walls | 1.5 m high | Too short for a realistic kitchen and visually reads as a low partition | Raise to 2.4 m; move wall centers from z=0.75 to z=1.20 |
| Kitchen island | 1.6 × 0.7 × 0.9 m | Plausible residential scale | Keep |
| Table | 0.8 × 0.8 × 0.7 m | Small but plausible; still leaves generous robot clearance | Keep for this pass |
| Chairs | 0.35 × 0.35 × 0.4 m single boxes | Obvious placeholder geometry rather than realistic furniture | Replace with the repository's existing `model://Chair` asset |
| Room footprint | 6 × 6 m | Plausible and comfortably larger than the ~0.36 m robot | Keep |

## Validation status

- **Static SDF / dimensional audit:** completed.
- **Asset URI check:** the same `model://Chair` asset is already used by `living_room.world`, so this is consistent with the package's established model-loading pattern.
- **Gazebo GUI visual inspection:** **not claimed in this environment**. A local ROS 2 Jazzy / Gazebo Harmonic launch should still be run before presenting the world as visually validated.

Suggested command:

```bash
ros2 launch oomwoo_gazebo world.launch.py world:=kitchen.sdf
```

During the GUI pass, check chair orientation / floor contact, island-to-wall clearance, robot spawn clearance, and whether any furniture intersects the walls.