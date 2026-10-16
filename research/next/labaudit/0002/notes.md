# Lab audit, family 0002 (captured_0002; one render only, 49 frames, 24 fps, 1280x720, SAM green-screen composite)

Scene: the same white board as family 0001 (about 24 cm wide, rounded corners) leans on the lab table with its top far from the camera.
A pale orange ball is held at the top edge for frames 0-26. This is not the red 7 cm ball of 0027/0030, which has H=7 and S=210, while this ball has H=18 and S=124.
The ball starts rolling at frame 27-28 and rolls down the face of the board. On the board it is semi-transparent: the composite fades it.
It reaches the bottom edge at frame about 35.5, rolls toward the front of the table (frames 36-40), leaves the front edge at frame 41 and falls (frames 42-44).
Camera model: f=711, cx=640, cy=360, depths treated as range along the click ray.

Scripts are in scripts/:
- ballsize.py, ballcircle.py, ballprof.py: ball silhouette size
- board.py: board mask
- table.py, table2.py, tplane.py, tablegeo.py: table edges, plane, scale
- track.py, track_board.py: 2D tracks
- disp.py: displacement
- slope.py: slope length routes
- balltable.py, ballfall.py, fallgeo.py: ball on the table and the falling ball

Images: montage.png, zoom_*.png, motion_30_45.png, others_*.png.

## Geometry checks
- Board edges (frame 48): the top edge is at y 291-297, the bottom edge at y 416-423, the left edge at x 559->563 and the right edge at x 657->665.
  Corner-extrapolated widths are 97.7 px at the top and 103 px at the bottom.
- With the stated depths, the board is 24.9 cm wide at the top (1.815) and 24.2 cm at the bottom (1.6715). Family 0001 gave 24.0 for both.
  The stated far-end range therefore looks about 3% too far, a ToF edge or mixed-pixel effect. The near end is consistent.
- Table top rectification (front edge = 60.3 cm side): the aspect matches for f of about 711-730.
  At f=711 the board bottom range on the table plane is 1.59, about 5% short of the stated 1.6715. The table-scale route is therefore 3-5% "small" versus the ToF scale.
- The stated ball depths fit the slope: the range interpolated along the board, offset so that the t=1.0 ball is 1.779, reaches 1.736 at clip frame 31.1.
  This is t=1.30 s on the clip clock (1.3*24=31.2), so the clip time equals the label time here.

## Rows
| qid | question | current | my routes | verdict |
|---|---|---|---|---|
| 2146 | ball size (mm) | 52.8 | A: silhouette circle fit at frames 0-24 gives 25.4 px at the 50% edge level and 24.0 px at 70%. With the stated depth 1.779 and f=711 that is 60.0-63.5 mm. B: table-plane scale, where the board is 23.0 cm wide, times the ratio of the ball to the board top width: 58-60 mm. C: falling ball (frames 43/44 against green: 29.3/31.7 px) at modelled ranges of 1.26-1.32 on the table scale: 53-58 mm, or 55-61 on the ToF scale. Frame-41 width measures 27-28.6 px, giving 51-56 mm. | Left alone. Most likely 55-62. The current value may be about 10% low (its source measured about 21.9 px instead of 24-25.4). The routes spread over 53-63.5, and the two that agree (A and B, about 60) are only 14% above the current value, so the 15% gate is not met. |
| 2147 | slope length | 30.80 (pooled; identical to 0001) | Stated depths with the board edge midpoints: 33.7 cm (f=711) and 33.0 (f=730). Clicks 3 or 6 px inside the edges: 32.4 or 31.1. Physical routes: table scale 30.2; near-end ToF plus the width ratio 31.8. Family 0001 measured the same board at 31.8-32.0. | OK. Within about 10% at worst; the label is perhaps 31-34. |
| 2148 | displacement 1.0-1.3 s | 11.08 | Frame 24 (616.5,282.7) at 1.779 to frame 31-31.2 (617.5,317.9 to 335.3) at 1.736 gives 9.6-10.4 cm. Taking t=1.3 as frame 32 instead gives 13.6. | OK. 6-10% from the frame-31 value; this is a motion row and is not grossly off. |
| 2149 | v at 1.3 s | 102.6 | Slope-plane 3D track steps of 3.4, 4.7, 5.1, 6.2, 7.3 cm per clip frame (frames 30-35). The forward difference 1.30->1.34 s is about 4.6 cm/0.04 s, about 115 cm/s. | OK; not grossly off, so left alone under the rules. |
| 2150 | v at end of slope | 181.6 | Last step on the board is 7.3 cm/frame (176 cm/s at 24 fps). Extrapolating to the bottom gives about 200. sqrt(2*4.05*0.31-0.34) = 158-166. | OK; not grossly off, so left alone. |

## Result
No fixes for family 0002. The only row worth a second look is 2146 (ball size).
The evidence leans toward a label of about 58-62 mm, but it does not clear the two-route, 15% gate: route C, the physical size from the rolling and falling ball, sits closer to the current 52.8.
