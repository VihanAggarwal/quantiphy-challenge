# Lab audit, family 0009 (captured_0009 / 0009s / 0009x; 49 frames, 24 fps, 1280x720)

Scene: a woman holds a basketball at about shoulder height with her arms out. The ball stays still for frames 0-26.
It is released at about frame 27 (1.13 s), falls almost straight down, and bounces at frame 37 (1.54 s). This is the
lowest image position, and the ball bottom is at y~717, at the frame edge. The ball then rises to its apex at frame 46
(1.917 s, which matches the stated "t=1.92s max rebounce") and starts to fall again.
The s render (green background) and x render (white background, segmented) have exactly the same ball pixels as each
other and as the o render. All three share one label set.
Camera: f=711, cx=640, cy=360. The depth_info values are treated as ranges along the click ray.

Scripts: scripts/extract.py (frames), scripts/track.py (x-render mask, RANSAC circle fit on hull points; result in track_x.npy),
scripts/geom.py (labelled-range back-projection, drop line, rebound fits), scripts/vp.py (vertical vanishing point from wall
panel seams), scripts/heights.py (height routes across f = 700/711/722).
Images: montage_{o,s,x}.png, bounce_o.png, zoom_x_36_39.png, clahe48.png, gx48.png, ref_0035a_f00.png.

## Geometry
- Ball radius in pixels: 67.8 at frame 0, 53.6-54.2 at frames 43-44 (t=1.8 s), 55.2 at frame 46. Combined with the stated ranges
  1.321 / 1.5835 / 1.5795, this gives D = 23.9 / 23.3 / 23.9 cm, so the stated ranges sit at about the ball centre.
  With D=23.2, the size-based ranges are 1.283 (t=0), 1.589 (1.8 s) and 1.537 (1.92 s), within 3% of the stated values.
- Down direction, route 1: labelled P0 -> P46 (ball rays times the stated ranges), d=(0.055,0.894,0.445), camera pitch 26.4 deg.
  The size-based positions give the same direction. Every drop and rebound frame lies within 2 cm of this line.
- Down direction, route 2: vanishing point of the vertical wall panel seams (5 lines on frames 24 and 48, 3 on frame 0) at
  (735, 1900-1936), pitch 24.2-24.7 deg. This is about 2 deg from route 1.
- Floor point directly below the t=0 ball at range 2.0285: pixel (560,690). That is where the ball lands
  (frame 37 ball centre is about (547,660-668)), so the floor click was most likely at the bounce spot under the ball.

## Rows (identical for 0009, 0009s, 0009x)
| qids | question | current | my routes | verdict |
|---|---|---|---|---|
| 2176/2181/2186 | initial height above floor (cm) | 129.51 | (A) floor at 2.0285 straight below P0: 129.4 (route-1 down), 132.6-133.5 (VP down); (B) bounce frame 37 (width-based range 1.92-1.93) plus r: 127.9-129.8 at f=711, 127-130.5 over f 700-722 | OK (all routes within -2%/+3%) |
| 2177/2182/2187 | basketball diameter (cm) | 23.2 | stated basketball prior in 0035 (23.2; the same orange basketball appears in 0035a); circle fit with stated ranges 23.3-23.9 | OK (within 3%) |
| 2178/2183/2188 | max rebound height (cm) | 64.56 | (A) floor-range route: 65.6 (route-1 down), 68.8-69.7 (VP down); (B) bounce route: 64.1-66.0 at f=711 (62.6-67.4 over f) | OK (within 8%) |
| 2179/2184/2189 | velocity at 1.8 s (m/s) | 1.250 / 1.261 / 0.95 | 3D rebound track (frames 38-48) in video time: v(1.8)=0.93 (free fit), 0.85-0.99 (g fixed at 9.8); forward difference 43->44: about 0.83; physics with the apex at 1.917-1.92 s: 9.8 x 0.12 = 1.15-1.18 | not grossly off (<1.5x); left alone per rules |
| 2180/2185/2190 | distance from camera at 1.8 s (m) | 1.5835 | stated in depth_info; size route 1.589, line route about 1.61 | OK |

Notes and caveats:
- The geometric rebound has an effective g of 8.0-8.1 m/s^2 in 24-fps video time. The second differences are regular, with no
  duplicated frames in 38-48. So either the video time base is about 10% slow, or the length scale is off. The length scale
  is anchored by the ToF ranges and the 23.2 cm ball, and the labels use the same scale, so the heights are not affected.
  This only explains why the geometric v(1.8) (0.93) sits below the physics v(1.8) (1.15).
- The speed answers are inconsistent across renders: o/s have the label-noise factor applied (1.25/1.26), but x does not (0.95).
  All three renders share one label. The spread is 1.32x, below the 1.5x threshold, so I did not touch them per the rules.
  The orchestrator may want to unify them.

Result: no fixes for family 0009.
