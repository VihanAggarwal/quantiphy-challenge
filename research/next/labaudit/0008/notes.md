# Lab audit, family 0008 (captured_0008, 0008s, 0008x; 49 frames, 24 fps, 1280x720)

Scene: a person holds the lab basketball (Wilson, the same ball as captured_0035, which states 23.2 cm) above the lab
table. She holds it still in frames 0-20. The ball starts to move at frame ~21 (t ~0.87 s), leaves the hands by frame
23-24, falls onto the table top (contact at t ~1.225 s, between frames 29 and 30), bounces to an apex at frames 35-36
(t ~1.49 s), and lands again at frame ~41.3. The s and x renders have the same ball track to within 1-2 px. They
share one label set.

Camera: f=711, cx=640, cy=360. Depths are treated as range along the click ray.
Scripts (scripts/):
- extract.py: frames and montage
- track.py, circfit.py: colour-mask ball track
- edges.py: table edge lines and corners
- geom.py: plane normal from vanishing points
- heights.py, locus.py, emu.py: label emulation with the stated depths
- vline.py: heights along the vertical through the contact point, with a gravity check
- t0.py: height of the held ball
- sens.py: sensitivity to f and click positions
- ballistic.py: unconstrained 3D ballistic fit. It is ill-conditioned, so it is not used.
Images: montage.png, montage_20_31.png, zoom_27_32.png, zoom_release.png, table_grid.png, renders_f24.png.

## Geometry checks
- Table top corners (frame 10, fitted edge lines, residuals < 0.5 px): BL (477.7,415.9), BR (690.3,375.6),
  FR (757.1,540.8), FL (431.5,604.6). Back and front edges are nearly parallel. The side edges meet at (564,63).
- Plane normal (camera frame), from the vanishing points: (-0.161,-0.905,-0.395). The side directions are orthogonal
  at f=711 (cos -0.003).
- Rectified aspect (depth/width) is 1.244 at f=711 and 1.261 at f=722, against 76.0/60.3 = 1.260 for the lab table.
  This is the lab table. The camera sits h = 0.854 m above the table plane (0.849 from the width, 0.860 from the depth).
- Scale check by gravity: ball heights along the vertical through the contact point (frames 24-29), fitted with a
  free parabola, give g = 9.88 m/s^2 on the n/24 clock. This confirms the plane scale. With g fixed at 9.8: contact at
  t = 1.225 s; the extrapolated release from rest is at t = 0.85 s, 80.8 cm above the desk.
- The stated desk range of 1.725 m lies on the table across its middle-back: from (460,490) to (712,430). The foot of
  the ball's vertical at t = 1.0 s is at (595,449), where the range is 1.734. The impact point is at (587,461),
  range 1.693. So the desk click was very likely at or near the point below the ball.
- Clock: frame 24 is t = 1.0 s both on the n/24 clock and on the 25-fps capture clock (one frame dropped after
  frame 11, so (24+1)/25 = 1.0). The stated t = 1.5 s "max rebounce" matches the observed apex at 1.49 s, so there is
  no time offset.

## Rows
| qids | question | current | my routes | verdict |
|---|---|---|---|---|
| 2161/2166/2171 | initial ball-desk distance | 80.98 | Route A (label emulation at the stated time: ball at frame 24 (532,157) @1.401, desk point @1.725 on the table near the foot or impact point): 70.9-72.8, central 71.4. The full range over f 700-722, ball click +-5 px and desk u 560-640 is 70.2-73.2. Route B (physical height of the ball centre above the plane at t = 1.0 s): 69.2 from the stated range, 69.5-69.8 from the vertical line with g, 69.5 from free-fall timing. | Current is about 13% HIGH, but this is below the 15% gate, so NO FIX. Why it is off: the value is the R4 emulation (research/labdist). R4 put the ball at its t = 0 rest position (frames 0-20, centre 80.5-81 cm above the desk), with a depth scaled from the box, instead of the ball at the stated t = 1.0 s. At t = 1.0 s the ball has already dropped about 11 cm and moves at 1.5 m/s. The stated 1.401 also fits the frame-24 ball's apparent size (r = 59 px), not the held ball (r = 65 px, about 10% closer). R4's desk click (570,435)@1.725 is also 9.5 cm above the table surface, because the plane range there is 1.82. If the 15% gate is read relative to the new value with route B (69.5), the gap is 16.5%. A fix to about 71 would be justified under that reading. |
| 2162/2167/2172 | diameter | 23.2 (stated fact, 0035) | 2r*range/f with the stated range: 23.3 (frame 24) and 24.6 (apex). With the range taken to the front surface: 25.5 and 26.8. | OK (stated prior for the same lab ball) |
| 2163/2168/2173 | max rebound height wrt desk | 36.57 | Route A (apex (548,305)@1.5225, desk on the 1.725 locus near the foot or impact point): 39.7-41.5. With R4's desk click: 36.0-36.7. Route B (physical centre height at the apex): 38.3 (parabola), 39.2 (vertical line), 36.4-39.9 (stated range, surface or centre). | OK (within about 10%) |
| 2164/2169/2174 | v at 1.2 s | 4.27 / 4.10 / 4.39 | Physical speed: 3.43 m/s (vertical-line fit, n/24 clock), or about 3.6 on the 25-fps clock. The current values are x1.2-1.28 of that, which matches the label-noise correction. | Not grossly off; left alone per the rules |
| 2165/2170/2175 | ball-camera distance at 1.2 s | 1.564 | Stated in depth_info | OK |

Result: no fixes for family 0008. One flag for the orchestrator: the initial-distance rows (2161/2166/2171) are
probably about 12-13% high, from a wrong-time artefact in R4. Both routes give 69-73 cm. The gap is just under the
15% gate, so no change is proposed here.
