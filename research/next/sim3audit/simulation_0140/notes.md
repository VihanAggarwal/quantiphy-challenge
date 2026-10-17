# sim3audit: simulation_0140 family (simulation_0030, simulation_0030_segmented, simulation_0140)

Result: 8 rows checked, **no fixes proposed**.

## Family structure
- The family grouping is an artifact. Row 1501 (simulation_0030) carries the depth_info of simulation_0140
  (bird 25.328/24.899 m, neon sign 34.5 m), but simulation_0030 is the beach/eagle scene (960x960, eagle over a sand island).
  0030 and 0140 are different Blender scenes and share no object. 0030_segmented is the same footage as 0030
  (eagle bbox identical frame by frame). Its depth_info (eagle 106.642 m at t=1, 111.231 m at t=2) is the real one for 0030:
  the pixel speed falls 15.7 -> 15.1 px/frame (about 3-4 %/s), which matches a receding eagle (dr/r about 4.2 %/s), and not
  the approaching 25 m bird.
- So 0140 is effectively a singleton, and 0030/0030_seg belong with the beach eagle family (0023/0025/0028/0029/0031/0034/0035/0039).

## Eagle length (1501, 2010; current 0.8, pre-agent pipeline)
- Stated fact elsewhere in the beach family: simulation_0028 prior "length of the eagle = 0.8m" (same eagle asset).
- Re-measurement (scripts/eagle30.py): straight-line fit to the true depths (106.6/111.2 m, 12 m/s) gives a transverse speed of about 11.5 m/s
  at t=0.5 s. The pixel speed is about 376 px/s at 24 fps, so the scale is about 0.0306 m/px. The 0030 agent's body extent of 22-25 px then gives 0.67-0.77 m,
  and the 0.8 m asset would be about 26 px. That is consistent within about 10 %, and 0.8 is the stated-fact value. Keep 0.8.
- The 0030 agent used the wrong (copied) depth_info, but its scale came almost entirely from the speed prior, so 0.77 was barely affected.

## simulation_0140 (singleton): bird arc + "BE DIFFERENT" sign + facade windows
- Track (scripts/track140.py, fit140.py): median background, largest diff blob. Circle with constant angular speed:
  centre (1122, 1462), R = 1086 px, 21.22 deg/s (21.36 -> 21.10 over 4 s, flat), radius trend ~0. Pixel speed is 402 px/s. The arc over 99 frames is
  87.5 deg = 1659 px. Positions are t=0 (210, 872) and t=0.5 (335, 714). These match the agent's numbers.
- f from the depth ratio with constant Z (Euclidean range): f^2 = (r0^2 - rho r1^2)/(rho-1) gives f = 2605 px (agent 2610-2660; Blender 50 mm = 2667).
  A shared origin offset of 10 px changes f by <1 %. Range-vs-Z: a Z-convention would mean the pixel speed and radius drift by ~3 %/s. Neither drifts,
  so the Euclidean range with a frontal path plane is self-consistent. Z_bird = 24.16-24.30 m.
- Geometry check: the bird starts at the left-wall window (x = 192 px gives X = -7.1 m) and the facade/left-wall junction (x = 430 px at Z = 34.4) gives X = -7.0 m.
  At frame 99 the bird is at X = +6.6 m, near the right wall (+7.1 m). So the path runs from wall to wall and the traversed arc is the whole path.
- Window route: the facade opening is 121-125 px wide (profile 124-130 px including the groove shadow) and 164 px tall (h/w 1.27-1.36).
  If the 1.48 m frame filled the opening at Z = 34.4, then f = 2800-2900. The bird route says the frame is about 114 px (inset in the recessed opening).
  The two routes differ by 6-10 % in scale.

| qid | quantity | current | bird-f route (f 2605-2640) | window-prior route | verdict |
|---|---|---|---|---|---|
| 1502 | window frame height | 2.05 | n/a | 1.48 x (164/121..125) = 1.94-2.01 | keep (<6 %) |
| 1503 | sign width | 9.03 | 694 px x 34.37/f = 9.04-9.16 | 694/121..125 x 1.48 = 8.2-8.5 | keep (<10 %) |
| 1504 | sign height | 1.05 | 80-81 px gives 1.05-1.07 | 0.95-0.99 | keep |
| 1505 | path-to-wall distance | 10.2 | 34.37 - 24.16..24.30 = 10.1-10.2 | same | keep |
| 1506 | path length | 15.2 | 1659 px x Z/f = 15.2-15.4 (wall-to-wall arc) | 14.4 | keep |
| 1507 | speed at 1.0 s | 3.70 | 402 x Z/f = 3.68-3.73 (constant speed) | 3.5 | keep |

No row has two independent routes that agree within 8 % on a value that differs from the current one by >= 15 %.
