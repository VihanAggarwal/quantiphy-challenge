# simulation_0024 - fishing boat "AH805" (V3MS, 960x960, 75 frames @24 fps)

## Scale / camera
- Boat translates leftward, rigidly, no rotation (template track: -6.46 px/frame in x, -0.26 px/frame in y; t=1 -> t=2 displacement 155.2 px).
- Focal length from depth_info + speed: 4 m chord between rays at D1=90.1103, D2=90.4360 -> ray angle 0.04416 rad -> f = 3513 px (HFOV 15.6 deg); same for range or Z convention.
- Translational SfM (KLT tracks, f=3513, |v|=4 m/s): camera-frame velocity m = (-3.970, -0.148, +0.433) m/s. mz is confirmed by vertical scale change (0.427 m/s).
  That supports the RANGE depth convention (with Z convention mz would be 0.326); the origin sits at about u=570 at t=1.5.
- Pitch phi (camera view vs boat deck plane), several routes: zero-roll horizontal motion 18.9; mast parallax 17.0 (full) / 19.6 (lower part);
  antenna 17.8; stern pole 19.8; rail-post mirror pair 20.0; mast-top/rudder centre-plane 18.5; bow/mast 17.5. Adopted phi = 18.7 deg (+-1).

## Measurements (frame 36 coords)
- Length: bow stem head x=337 (y 530, Z 90.69 by SfM) to stern extreme x=731 (y 605). Solved in 3D along the motion direction: L = 10.20 m (barely depends on phi).
- Height: mast top y=298.4 (x=509, Z 88.31 by mast parallax) to rudder-blade bottom y=659.7 (x=713, Z 90.75; the rudder blade is stable over frames,
  so it is not a reflection). Vertical separation along world up: H = 9.50 m (9.42-9.55 for phi 17-19.5).
- Width: gap between the far gunwale outer top (silhouette vs background) and the near gunwale outer edge (cap top +~2 px), matched by station.
  The gap is 40-41 px at both ends of the wheelhouse; the extrapolated maximum under the wheelhouse is about 44 +- 1.5 px.
  W = gap / ((f/Z) * (0.994 sin phi + b*|t_z|)) with Z~90.3 -> 3.33 m at phi=18.7. Rail-pair parallax scaling gives 3.16; phi=17 would give 3.6.

## Answers / confidence
- 1106 height 9.5 m: medium. Assumes no hidden submerged keel below the visible rudder.
- 1107 length 10.2 m: high.
- 1108 width 3.3 m: medium-low. Sensitive to pitch (+-1 deg = +-5%) and to the beam location hidden behind the wheelhouse.
