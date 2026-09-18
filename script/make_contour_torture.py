#!/usr/bin/env python3
# Copyright 2026 OOMWOO
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Generate worlds/contour_torture.world: three "combs" for a wall follower.

Every obstacle is defined once, below, as boxes and cylinders. The script writes
the SDF, audits every gap between features against the robot's size, and can
draw a top-down preview, so the layout is checked by arithmetic rather than by
eye. Edit the layout here, not in the .world file.

    python3 script/make_contour_torture.py            # write the world + audit
    python3 script/make_contour_torture.py --png FILE  # also draw the layout

The room is a compact 6 x 6 m, x and y in [-3, 3], with a PENINSULA jutting in
from the east wall that folds the course back on itself: the boundary stays one
continuous wall, so the follower traces the perimeter and both faces of the
peninsula without ever having to choose. That packs 33 m of wall into 36 m^2,
and the whole course fits on screen.

The follower keeps the wall on its RIGHT and the robot spawns facing +x, so it
runs anticlockwise:

    south wall, heading +x    comb A: four square teeth, gaps 2.0d, 1.1d, 0.9d
    east wall, heading +y     comb B: a small block, then a wide one
    peninsula south face      comb B: a leg, two legs in a row, two thick legs
    peninsula tip             a 180 deg wrap, the sharpest convex turn here
    peninsula north face      comb C: blocks standing 0.25 m and 0.50 m off it
    east wall again           a convex half-cylinder
    north wall, heading -x    comb C: wedge, concave bay R 0.35, convex R 0.15
    west wall, heading -y     comb C: concave bay R 0.17 (too tight), V trap
    south wall again          back to the start

    ros2 launch oomwoo_gazebo world.launch.py world:=contour_torture.world \\
        x_pose:=-2.6 y_pose:=-2.77 odom_source:=robot_wheels
"""

import argparse
import math
import os
import sys

ROBOT_D = 0.349            # oomwoo-one base diameter
BUMPER_R = 0.1814          # what touches first: the bumper facets' corners
STANDOFF = 0.23            # contour_follower default
WALL_T = 0.4               # thick, so half-buried wedges and arcs stay hidden
WALL_H = 0.5
OBST_H = 0.3               # everything is well above the 8.8 cm scan plane
X0, X1, Y0, Y1 = -3.0, 3.0, -3.0, 3.0
FIN_Y, FIN_T, FIN_X = 0.0, 0.10, -1.4   # peninsula: centre line, thickness, tip

# ---------------------------------------------------------------- primitives
# ('box', cx, cy, sx, sy, yaw) or ('cyl', cx, cy, r); grouped into features.
FEATURES = []          # (name, colour, [primitives], note)


def feature(name, colour, prims, note=''):
    FEATURES.append((name, colour, prims, note))


def box(x0, x1, y0, y1):
    """Axis-aligned box from its extents."""
    return ('box', (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0)


def board(p, q, thick, side):
    """
    A thin box whose one face lies exactly on the segment p-q.

    side = +1 puts the box's body to the LEFT of p->q, -1 to the right, so the
    face the robot meets is exactly where the drawing says it is.
    """
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * side, dx / length * side
    cx = (p[0] + q[0]) / 2 + nx * thick / 2
    cy = (p[1] + q[1]) / 2 + ny * thick / 2
    return ('box', cx, cy, length, thick, math.atan2(dy, dx))


def bay(xc, yfront, radius, inward, segs=14, thick=0.04):
    """
    A semicircular bay of the given radius, opening toward the room.

    Built from short boards laid along the arc, each with its inner face on the
    circle, overlapping slightly so the surface is continuous. inward is the
    direction from the room into the wall (+1 for the north wall).
    """
    prims = []
    for i in range(segs):
        a0 = math.pi * i / segs
        a1 = math.pi * (i + 1) / segs
        p = (xc + radius * math.cos(a0), yfront + inward * radius * math.sin(a0))
        q = (xc + radius * math.cos(a1), yfront + inward * radius * math.sin(a1))
        mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        grow = 0.06                              # overlap neighbours
        ux, uy = q[0] - p[0], q[1] - p[1]
        ln = math.hypot(ux, uy)
        p = (mid[0] - ux / ln * (ln / 2 + grow / 2), mid[1] - uy / ln * (ln / 2 + grow / 2))
        q = (mid[0] + ux / ln * (ln / 2 + grow / 2), mid[1] + uy / ln * (ln / 2 + grow / 2))
        # body on the far side of the arc from the room
        prims.append(board(p, q, thick, -inward))
    return prims


# ---------------------------------------------------------------- the room
feature('wall_south', 'wall', [box(X0 - WALL_T, X1 + WALL_T, Y0 - WALL_T, Y0)])
feature('wall_north', 'wall', [box(X0 - WALL_T, X1 + WALL_T, Y1, Y1 + WALL_T)])
feature('wall_west', 'wall', [box(X0 - WALL_T, X0, Y0, Y1)])
feature('wall_east', 'wall', [box(X1, X1 + WALL_T, Y0, Y1)])

# ---------------------------------------------------------------- comb A
# South wall, robot heading +x. Square teeth D deep and D wide. Around each one
# the path is: CCW 90, straight D, CW 90, straight D, CW 90, straight D, CCW 90,
# then along the wall for the gap W before the next tooth. Four teeth give three
# gaps, narrowing from roomy to impossible.
D = 0.45
gaps = [('2.0d', 2.0 * ROBOT_D), ('1.1d', 1.1 * ROBOT_D), ('0.9d', 0.9 * ROBOT_D)]
x = -1.8
for i in range(4):
    note = 'gap after it: %s = %.3f m' % gaps[i] if i < 3 else ''
    feature('A%d_tooth' % (i + 1), 'combA', [box(x, x + D, Y0, Y0 + D)], note)
    if i < 3:
        x += D + gaps[i][1]

# ------------------------------------------------------------- the peninsula
# Juts in from the east wall and folds the course: the robot follows the east
# wall north, turns in along the south face, wraps the tip, and comes back east
# along the north face before carrying on up the east wall.
feature('peninsula', 'wall',
        [box(FIN_X, X1, FIN_Y - FIN_T / 2, FIN_Y + FIN_T / 2)],
        '4.4 m x 0.1 m; its tip is a 180 deg wrap')

# ---------------------------------------------------------------- comb B
# East wall below the peninsula, then along the peninsula's south face.
feature('B1_block_small', 'combB', [box(X1 - 0.3, X1, -2.3, -2.1)],
        '0.3 deep x 0.2 wide')
feature('B2_block_wide', 'combB', [box(X1 - 0.3, X1, -1.5, -0.9)],
        '0.3 deep x 0.6 wide')
leg_gap = 0.25                     # leg to surface: too narrow to pass behind
ly = FIN_Y - FIN_T / 2 - leg_gap - 0.02
feature('B3_leg', 'leg', [('cyl', 2.3, ly, 0.02)],
        '4 cm leg, %.2f m below the peninsula' % leg_gap)
feature('B4_legs_pair', 'leg', [('cyl', 1.3, ly, 0.02), ('cyl', 1.3, ly - 0.5, 0.02)],
        'two 4 cm legs in a row, 0.46 m apart (passable between)')
feature('B5_thick_legs_pair', 'leg',
        [('cyl', 0.2, ly - 0.03, 0.05), ('cyl', 0.2, ly - 0.53, 0.05)],
        'two 10 cm legs in a row, 0.40 m apart (tight)')

# ---------------------------------------------------------------- comb C
# The peninsula's north face, then the east, north and west walls.
nf = FIN_Y + FIN_T / 2
feature('C2_block_gap_025', 'combC', [box(-0.85, -0.35, nf + 0.25, nf + 0.45)],
        'free-standing, 0.25 m off the peninsula: too narrow to pass behind')
feature('C3_block_gap_050', 'combC', [box(0.55, 1.05, nf + 0.50, nf + 0.70)],
        'free-standing, 0.50 m off the peninsula: passable behind')
feature('C4_convex_R035', 'combC', [('cyl', X1, 1.5, 0.35)],
        'convex half-cylinder, R = 0.35 (two robot radii), on the east wall')
feature('C1_wedge', 'combC', [('box', 1.6, Y1, 0.4, 0.4, math.pi / 4)],
        '90 deg wedge jutting 0.28 m (a square half buried in the wall)')
# concave bay R 0.35 set into a 0.5 m ledge on the north wall
xc, front = 0.0, Y1 - 0.5
feature('C5_concave_R035', 'combC',
        [box(xc + 0.35, xc + 0.65, front, Y1), box(xc - 0.65, xc - 0.35, front, Y1)]
        + bay(xc, front, 0.35, +1),
        'concave bay, R = 0.35: the robot fits, with ~5 cm to spare')
feature('C6_convex_R015', 'combC', [('cyl', -1.6, Y1, 0.15)],
        'convex half-cylinder, R = 0.15: a tight outside curve')
# West wall, robot heading -y: a bay it cannot enter, then the trap. The bay is
# the north-wall one turned a quarter turn, hence the swapped box dimensions.
# Both sit in the northern half, so the run back to the start stays plain wall.
yc, wfront = 1.6, X0 + 0.3
feature('C7_concave_R017', 'combC',
        [box(X0, wfront, yc + 0.17, yc + 0.47), box(X0, wfront, yc - 0.47, yc - 0.17)]
        + [('box', p[2], p[1], p[4], p[3], -p[5]) for p in bay(yc, wfront, 0.17, +1)],
        'concave bay, R = 0.17: 0.34 m wide, the robot does NOT fit')
# V trap in a 0.5 m ledge. Its ledge runs up to meet the bay's, so the step
# between them is an inside corner rather than a slot, and stops short of the
# south-west corner, so the robot's way home is clear wall.
yv, half, vfront = 0.2, 0.4, X0 + 0.5
feature('C8_v_trap', 'combC',
        [box(X0, vfront, yv + half, yc - 0.47), box(X0, vfront, -0.6, yv - half),
         board((vfront, yv - half), (X0, yv), 0.08, -1),
         board((X0, yv), (vfront, yv + half), 0.08, -1)],
        'V pocket 0.8 m wide x 0.5 m deep: in you go, and it narrows')

# ---------------------------------------------------------------- output

COLOURS = {'wall': '0.75 0.75 0.78 1', 'combA': '0.55 0.35 0.20 1',
           'combB': '0.30 0.50 0.70 1', 'leg': '0.40 0.25 0.15 1',
           'combC': '0.50 0.62 0.45 1'}

HEADER = """<?xml version="1.0" ?>
<!--
  Contour-following torture course, generated by script/make_contour_torture.py.
  Edit the layout there and re-run it; hand edits here will be overwritten.

  A compact 6 x 6 m room with a PENINSULA jutting in from the east wall, which
  folds the course back on itself: one continuous boundary, 33 m of wall inside
  36 m^2, and it all fits on screen. The follower keeps the wall on its right and
  the robot spawns facing +x, so it runs anticlockwise:

    south wall          comb A: four square teeth, gaps 2.0d, 1.1d, 0.9d
    east wall           comb B: a small block, then a wide one
    peninsula, south    comb B: a leg, two legs in a row, two thick legs
    peninsula tip       a 180 deg wrap, the sharpest convex turn here
    peninsula, north    comb C: blocks standing 0.25 m and 0.50 m off it
    east wall again     a convex half-cylinder
    north wall          comb C: wedge, concave bay R 0.35, convex R 0.15
    west wall           comb C: concave bay R 0.17 (too tight), then the V trap
    south wall again    back to the start

  Start it on the south wall:
    ros2 launch oomwoo_gazebo world.launch.py world:=contour_torture.world
        x_pose:=-2.6 y_pose:=-2.77 odom_source:=robot_wheels

  Some gaps are deliberately too narrow (d = robot diameter, 0.349 m):
%(squeezes)s
-->
<sdf version="1.10">
  <world name="default">
    <scene>
      <shadows>false</shadows>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
    </scene>
    <gui fullscreen="false">
      <camera name="user_camera">
        <pose>-6 0 7 0 0.85 0</pose>
        <view_controller>orbit</view_controller>
        <projection_type>perspective</projection_type>
      </camera>
    </gui>
    <physics type="ode">
      <real_time_update_rate>1000</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <ode>
        <solver>
          <type>quick</type>
          <iters>150</iters>
          <precon_iters>0</precon_iters>
          <sor>1.4</sor>
          <use_dynamic_moi_rescaling>true</use_dynamic_moi_rescaling>
        </solver>
        <constraints>
          <cfm>1e-05</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>2000</contact_max_correcting_vel>
          <contact_surface_layer>0.01</contact_surface_layer>
        </constraints>
      </ode>
    </physics>
    <plugin name="gz::sim::systems::Physics" filename="gz-sim-physics-system"/>
    <plugin name="gz::sim::systems::UserCommands" filename="gz-sim-user-commands-system"/>
    <plugin name="gz::sim::systems::SceneBroadcaster" filename="gz-sim-scene-broadcaster-system"/>
    <plugin name="gz::sim::systems::Sensors" filename="gz-sim-sensors-system">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin name="gz::sim::systems::Imu" filename="gz-sim-imu-system"/>
    <!-- Required for contact/bumper sensors to publish. A robot's model-level
         Contact plugin is a no-op; without this world-level system the contact
         topics exist but stay permanently silent. -->
    <plugin name="gz::sim::systems::Contact" filename="gz-sim-contact-system"/>
    <gravity>0 0 -9.8</gravity>
    <atmosphere type="adiabatic"/>

    <include>
      <uri>model://ground plane</uri>
      <name>ground_plane</name>
      <pose>0 0 0 0 0 0</pose>
    </include>

    <light name="sun" type="directional">
      <cast_shadows>false</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <intensity>3</intensity>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
"""


def shape_xml(prim, height):
    if prim[0] == 'box':
        _, cx, cy, sx, sy, yaw = prim
        geom = '<box><size>%.4f %.4f %.3f</size></box>' % (sx, sy, height)
        pose = '%.4f %.4f %.3f 0 0 %.5f' % (cx, cy, height / 2, yaw)
    else:
        _, cx, cy, r = prim
        geom = ('<cylinder><radius>%.4f</radius><length>%.3f</length></cylinder>'
                % (r, height))
        pose = '%.4f %.4f %.3f 0 0 0' % (cx, cy, height / 2)
    return pose, geom


def model_xml(name, colour, prims):
    height = WALL_H if colour == 'wall' else OBST_H
    parts = ['    <model name="%s">' % name, '      <static>true</static>',
             '      <link name="link">']
    for i, prim in enumerate(prims):
        pose, geom = shape_xml(prim, height)
        for kind in ('collision', 'visual'):
            parts.append('        <%s name="%s_%d">' % (kind, kind[:3], i))
            parts.append('          <pose>%s</pose>' % pose)
            parts.append('          <geometry>%s</geometry>' % geom)
            if kind == 'visual':
                parts.append('          <material><diffuse>%s</diffuse>'
                             '<ambient>%s</ambient></material>'
                             % (COLOURS[colour], COLOURS[colour]))
            parts.append('        </%s>' % kind)
    parts += ['      </link>', '    </model>', '']
    return '\n'.join(parts)


def outline(prims, step=0.01):
    """Sample a feature's footprint edges as points."""
    pts = []
    for prim in prims:
        if prim[0] == 'box':
            _, cx, cy, sx, sy, yaw = prim
            c, s = math.cos(yaw), math.sin(yaw)
            corners = [(-sx / 2, -sy / 2), (sx / 2, -sy / 2),
                       (sx / 2, sy / 2), (-sx / 2, sy / 2)]
            corners = [(cx + a * c - b * s, cy + a * s + b * c) for a, b in corners]
            for k in range(4):
                p, q = corners[k], corners[(k + 1) % 4]
                n = max(2, int(math.hypot(q[0] - p[0], q[1] - p[1]) / step))
                pts += [(p[0] + (q[0] - p[0]) * t / n, p[1] + (q[1] - p[1]) * t / n)
                        for t in range(n)]
        else:
            _, cx, cy, r = prim
            n = max(12, int(2 * math.pi * r / step))
            pts += [(cx + r * math.cos(2 * math.pi * k / n),
                     cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    return pts


def audit():
    """Every gap between two features narrower than the robot plus 10 cm."""
    import numpy as np
    clouds = [(n, np.array(outline(p))) for n, _c, p, _t in FEATURES]
    out = []
    for i, (na, pa) in enumerate(clouds):
        for nb, pb in clouds[i + 1:]:
            d2 = ((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1).min()
            gap = math.sqrt(d2)
            if 0.02 < gap < ROBOT_D + 0.10:
                out.append((gap, na, nb))
    # within-feature squeezes (pairs of legs) are listed from the notes instead
    return sorted(out)


def to_segments_and_circles():
    """The same layout for the 2D test harness: line segments and circles."""
    segs, circs = [], []
    for _n, _c, prims, _t in FEATURES:
        for prim in prims:
            if prim[0] == 'box':
                _, cx, cy, sx, sy, yaw = prim
                c, s = math.cos(yaw), math.sin(yaw)
                cs = [(-sx / 2, -sy / 2), (sx / 2, -sy / 2),
                      (sx / 2, sy / 2), (-sx / 2, sy / 2)]
                cs = [(cx + a * c - b * s, cy + a * s + b * c) for a, b in cs]
                segs += [(cs[k], cs[(k + 1) % 4]) for k in range(4)]
            else:
                circs.append(((prim[1], prim[2]), prim[3]))
    return segs, circs


def draw(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon
    fig, ax = plt.subplots(figsize=(9.5, 9.5))
    fills = {'wall': '#bfc0c6', 'combA': '#8c5a33', 'combB': '#4d80b3',
             'leg': '#66402a', 'combC': '#80a073'}
    for name, colour, prims, _t in FEATURES:
        for prim in prims:
            if prim[0] == 'box':
                _, cx, cy, sx, sy, yaw = prim
                c, s = math.cos(yaw), math.sin(yaw)
                cs = [(cx + a * c - b * s, cy + a * s + b * c)
                      for a, b in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2),
                                   (sx / 2, sy / 2), (-sx / 2, sy / 2))]
                ax.add_patch(Polygon(cs, closed=True, fc=fills[colour], ec='k', lw=0.4))
            else:
                ax.add_patch(Circle((prim[1], prim[2]), prim[3], fc=fills[colour],
                                    ec='k', lw=0.4))
        if colour != 'wall':
            xs = [p[1] for p in prims]
            ys = [p[2] for p in prims]
            lx, ly = sum(xs) / len(xs), sum(ys) / len(ys)
            if lx > 2.2:                                 # east wall: label inward
                pos, ha = (lx - 1.2, ly), 'right'
            else:
                pos, ha = (lx, ly + (0.55 if ly < 0 else -0.55)), 'center'
            ax.annotate(name, (lx, ly), pos, fontsize=7, ha=ha, va='center',
                        arrowprops=dict(arrowstyle='-', lw=0.4))
    ax.add_patch(Circle((-2.6, -2.77), ROBOT_D / 2, fc='#e8b400', ec='k', lw=0.6))
    ax.annotate('start, facing +x', (-2.6, -2.77), (-2.1, -1.9), fontsize=8,
                arrowprops=dict(arrowstyle='->', lw=0.6))
    ax.set_xlim(X0 - 0.6, X1 + 0.6)
    ax.set_ylim(Y0 - 0.6, Y1 + 0.6)
    ax.set_aspect('equal')
    ax.set_xticks(range(-3, 4))
    ax.set_yticks(range(-3, 4))
    ax.grid(True, lw=0.3)
    ax.set_title('contour_torture.world (top view, +x right). Robot runs anticlockwise.')
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--png', help='also draw the layout to this file')
    ap.add_argument('--out', default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'worlds',
        'contour_torture.world'))
    a = ap.parse_args()

    squeezes = audit()
    lines = ['    %-20s %-20s %.3f m%s' % (na, nb, g, '  (does not fit)' if g < ROBOT_D
                                              else '')
             for g, na, nb in squeezes]
    notes = ['    %-20s %s' % (n, t) for n, _c, _p, t in FEATURES if t]
    text = HEADER % {'squeezes': '\n'.join(lines) + '\n\n  Features:\n' + '\n'.join(notes)}
    text += '\n'.join(model_xml(n, c, p) for n, c, p, _t in FEATURES)
    text += '  </world>\n</sdf>\n'
    assert '--' not in text.split('<!--', 1)[1].split('-->', 1)[0], \
        'XML comments may not contain a double hyphen'
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

    print('wrote %s (%d features)' % (os.path.normpath(a.out), len(FEATURES)))
    print('gaps narrower than the robot + 10 cm (all intended):')
    for line in lines:
        print(line)
    if a.png:
        draw(a.png)
        print('drew %s' % a.png)
    return 0


if __name__ == '__main__':
    sys.exit(main())
