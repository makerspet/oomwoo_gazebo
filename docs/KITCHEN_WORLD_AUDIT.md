# Kitchen world geometry and navigation audit

`worlds/kitchen.world` contains only local SDF primitives plus the vendored
`model://KitchenMaterials` texture files. All structural collisions are simple
boxes or cylinders; visual detail is deliberately separate from navigation
collision where a high-detail collision would be harmful to a robot vacuum.

| Model(s) | Visual geometry / material | Collision geometry and dimensions (m) | State | Navigation and visual/collision notes |
|---|---|---|---|---|
| floor | Box, Brown Floor Tilles PBR | box 7.00 x 5.50 x 0.05 | static | Continuous traversable surface; visual texture does not affect collision. |
| doorway_landing | Box, matching Brown Floor Tilles PBR | box 1.00 x .90 x .05 | static | Extends the south threshold so the 1.0 m doorway is safely crossable rather than ending at a floor edge. |
| north/west/east/south walls | Boxes, neutral painted finish | north 7.00 x .10 x 2.50; sides .10 x 5.50 x 2.50; south segments 3.00 x .10 x 2.50 | static | South segments leave a 1.0 m doorway onto the landing. |
| north counter base / toe-kick / top | Boxes, oak fronts, dark plinth, granite top | base 3.40 x .56 x .77; toe-kick 3.40 x .48 x .13; top 3.50 x .66 x .045 | static | Plinth collision is recessed .04 m from base face, matching the visible toe-kick recess; solid counter prevents under-cabinet clipping. |
| east counter base / toe-kick / top | Boxes, oak fronts, dark plinth, granite top | base .56 x 2.10 x .77; toe-kick .48 x 2.10 x .13; top .66 x 2.20 x .045 | static | Same physical toe-kick recess as north run. |
| refrigerator | Cabinet box plus door/handle visual detail, metal PBR | box .92 x .78 x 1.90 | static | One conservative full footprint collision; handles are visual only. |
| range_oven | Appliance box plus glass door, burners, knobs | box .62 x .68 x .90 | static | Full base collision; small controls are nonblocking visuals. |
| sink_basin | Inset metallic box and faucet visuals | none | static | Counter base/top provide the robot collision; basin is visual recess only. |
| island base / top | Boxes, oak base and granite top | base 1.65 x .72 x .82; top 1.80 x .88 x .045 | static | Conservative continuous obstacle; recovered placement preserves more than 1 m circulation. |
| dining_table | Top and four-leg boxes, oak PBR | top 1.45 x .82 x .06; four legs .08 x .08 x .70 | static | Legs are individually collidable so open under-table volume is not falsely blocked. |
| chair_north / chair_south | Seat/back boxes, oak PBR | seat .45 x .45 x .08; back .45 x .07 x .60 | static | Furniture is deliberately physical; chairs constrain the dining approach. |
| sink_mat | Thin box, denim PBR | box .80 x .45 x .008 | static | Low, expected traversable-looking threshold; retained as a tiny physical height. |
| pet_bowl | Cylinder with colored inner bowl detail | cylinder r=.16, h=.06 | static | Low obstacle intended for lidar/contact checks. |
| toy_ball | Sphere, colored rubber-like material | sphere r=.10 | dynamic, 0.08 kg | Only intentional movable obstacle; no complex mesh collision. |

## Resource and collision conclusions

- No `<uri>`, `<mesh>`, texture map, or material map points to a remote source.
- The room has no visual mesh/collision mesh mismatch: all collision-bearing
  objects use primitive bounds that represent what a vacuum can physically hit.
- Small appliance and furniture features are visual-only where their collision
  would create spurious navigation obstacles; primary bases remain solid.
