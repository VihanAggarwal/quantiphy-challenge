# Lab audit, family 0006 (captured_0006 and captured_0006s; 49 frames, 24 fps, 1280x720)

Scene: a person stands behind the lab table and holds a yellow pineapple-character toy (its face is blurred; green leaves on top).
The toy is held still for frames 0-18. It is tossed up and forward from frame 19. The apparent apex is at frame 25 (t about 1.04 s).
It falls toward the camera and hits the table top near the front edge between frames 31 and 32 (t about 1.30-1.33 s).
It bounces (frames 33-35), rolls left along the front edge (frames 36-42), and falls off the front-left corner (frames 43-46).
The s render has the same geometry, but the background is replaced and the toy is semi-transparent in the air (frames 0-31).
From frame 32 on, its pixels match the o render. The o render was used for every measurement. Both renders share one set of labels.
Camera: f=711, c=(640,360). Stated ranges are treated as range along the click ray.

Scripts (scripts/): mask.py (yellow mask, bbox and centroid per frame), table.py (table-top edge lines and corners),
rectify.py (table aspect vs f), routeA.py (sizes at the stated range), routeB.py (table plane, toy contact points),
routeC.py (free-fall scale fit), motion.py (label-style displacement and speeds).
Images: montage.png and montage_s.png, fall_22_33.png, zoom_toy_air.png, zoom_land.png, toy_grid.png (6x, 10 px grid),
toy_fall_grid.png, toy_table_grid.png, table_fit.png.

## Geometry
- Table-top corners (frame 0, mask edges): BL (510.8,432.3), BR (814.2,433.6), FR (973.8,513.9), FL (394.7,511.1).
  The side edges meet at (638.6,345.5), so the camera is nearly level (about 1.2 deg of pitch).
- The wood grain runs front to back, as in family 0002, where the front edge is the 60.3 cm side. Taking the front edge as 60.3 cm puts
  the front edge at Z 0.741 and the camera 17.4 cm above the top.
  Caveat: at f=711 the depth sides rectify to 67.3 cm, not 76. The blurred back edge is probably a few pixels off.
  Taking the front edge as 76 cm instead gives a 76 x 84.8 table, and a landing point that would be farther away than the stated
  t=1.2 range, which is not possible. So the 60.3 front is the consistent choice.
- The toy's Z, taken as linear between the label range at f24 (Z 1.341) and the table landing contact at f32 (Z 0.889 on the plane),
  predicts Z 1.07 at t=1.2. The stated 1.065 (Z 1.040) agrees within 3%. The stated ranges and the table plane are therefore consistent.
- Free-fall scale (routeC) is weakly determined because the toy also moves toward the camera. It gives s 1.14-1.29 against the
  label-range model. It is not used for any decision.

## Rows
| qid (o/s) | question | current o / s | routes | verdict |
|---|---|---|---|---|
| 2151/2156 | toy height | 9.63 / 10.54 | A: f24 body 50.8 px at R 1.402 gives 9.13 cm; f25 gives 9.40; adding the leaves (about 5 px) gives 10.0-10.3. At t=1.2 (R 1.065), 55-65 px gives 8.0-9.5. B: table plane, toy lying on its side at f39-41 (long axis about 100-110 px with blur, Z 0.77) gives 10.8-11.4 | OK. Both renders fall inside the 9-11 cm band |
| 2152/2157 | toy width | 10.19 / 10.82 | A: f24 55.9 px gives 10.50 cm; f25 57.5 px gives 10.78. B: face-on at f35, 83 px at Z 0.77-0.89, gives 9.0-10.4. In the hand (f0), 41 px is consistent with Z about 1.8, the person's plane | OK |
| 2153/2158 | v at 1.2 s | 2.1 / 2.1 | Track with Z linear between the label range and the landing: forward differences 28->29 2.03, 28.8->29.8 2.43, 29->30 2.54 (24 fps). Physics (apex 1.02-1.04 s, Vz 1.37-1.5): 2.08 instantaneous, 2.24-2.47 forward difference | OK. Not grossly off; left alone |
| 2154/2159 | displacement 1.0->1.2 s | 36.28 / 36.38 | Stated ranges at the centre pixels: f24/f28.8 gives 35.8; f24/f29 gives 36.2; with 25-fps indexing (f25/f30), 40.9 | OK |
| 2155/2160 | v at first desk impact | 2.7 / 2.7 | Physics: vertical 2.55-3.07 plus Vz 1.37-1.5 gives 2.9-3.4. Forward difference 31->32 on the track: 2.8-2.9 | OK. At most about 1.25x off; motion rule, left alone |

The two renders carry different size answers (9.63 vs 10.54 and 10.19 vs 10.82) for one shared label. Both values are within about 10% of
routes A and B, and the gap is under the 15% gate, so nothing is changed. If pooling is wanted: height about 10.1, width about 10.5.

Result: no fixes for family 0006.
