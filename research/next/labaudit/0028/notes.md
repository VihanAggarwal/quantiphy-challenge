# Lab audit, family 0028 (captured_0028, 0028s, 0028x; 49 frames, 24 fps, 1280x720; one event, one label set)

Scene: a ping-pong ball (stated 40 mm) is held above the far half of the lab table (frames 0-20, x~718-722, y~290-312).
It is released at about frame 21 (vertex of the falling parabola at 20.9), falls and bounces on the table at about frame 26.2,
just in front of the back edge. The contact centre is at y~420, so the bottom is at ~430, while the back edge is at 426.
It peaks at frame 31.9 (y 300, x 750), bounces again at about frame 36.5-37 (bottom y~434, x~759), peaks at 41.7 and bounces at ~47.
Between bounces the ball drifts right and toward the camera, so later bounces sit lower in the image and the ball's width grows.
Camera: f=711, cx=640, cy=360; depth_info is taken as the range at the click.

Scripts are in scripts/:
- extract.py: frames and montage
- track.py: centroid track on the x render
- ballsize.py: half-max ball widths
- table2.py, rect.py, geo.py: table corners, rectification and plane
- fit.py, bounce.py: parabola fits, bounce and apex times
- motion.py: label-style emulation from the stated anchors

## Geometry checks
- Table corners (x render, frames 5/10/40), BL (574.5,424.0), BR (847.7,427.6), FR (964.0,495.1), FL (463.4,482.6), are stable to 1 px.
  At f=711 the rectified width/depth is 0.84; front=60.3 and depth=76.0 would give 0.79. The scale from the width and the scale from the depth differ by 6%.
  The camera is only ~17 cm above the table plane, an almost grazing view, so table-plane ranges near the back edge are very sensitive.
  Back edge at x 737 (y 426): range 1.60 (width scale) to 1.69 (depth scale). A contact point at y~430 gives ~1.53-1.62, consistent with the stated 1.557 at t=1.1.
- Ball size against the stated ranges: half-max widths are 19.6-19.8 px at frames 27-28 and 21.6-22.2 px at frames 31-32.
  The width ratio of 1.10 matches the stated range ratio of 1.557/1.4115 = 1.103, so the stated t=1.1 and t=1.3 ranges are internally consistent.
  The absolute widths read ~9% large, from the segmentation halo.
  At t=1.0 (frames 24-25) the width of 18.4-18.8 px implies ~1.65 on the same scale, against the stated 1.805, so the t=1.0 ToF reading looks ~9% far.
- Pixel accelerations: arc 1 is 7.2-7.6 px/frame^2, arc 2 is 8.8-9.1, and the pre-bounce fall is ~9 (noisy).
  Apex timing: frame 31.9, which is t=1.33 at 24 fps or 1.28 at 25 fps; both fit "1.3 s (max height)".

## Rows (the same label for all three renders)
| qids | question | current | my routes | verdict |
|---|---|---|---|---|
| 2479/2485/2491 | max height (cm) | 25.0 (set by labstatic 44->25) | Route A, table plane plus the stated apex range 1.4115 at (750,300): the ball centre is 26.6-27.5 cm above the table plane and its bottom 24.6-25.5. Route B, physics: rise time from bounce (26.2) to apex (31.9) is 5.65-5.74 frames, giving 26.7-27.6 cm at 24 fps or 24.6-25.5 at 25 fps. Route C, pixels: 120 px from bounce centre to apex at a mean range of ~1.48 gives ~25 cm. labstatic found 19-23 vertical and 24-27 as a 3D distance. | OK (within 10%) |
| 2478/2484/2490 | distance 1.1-1.3 s (cm) | 29.1 / 29.3 / 27.3 | Label emulation from the stated anchors plus my track: straight 24.7 (24 fps) or 20.7 (25 fps); path about 22-25 before ToF noise. Bounce-to-apex 3D is about 25-27. | Motion row, not grossly off; left alone |
| 2474/2480/2486 | v at 1.0 s (cm/s) | 385 / 397 / 385 | Emulation: 202-233 with a constant depth, 316-336 with depth interpolated between the 1.805 and 1.557 anchors. Physical speed is ~130-150, since the ball was dropped at frame ~21. The label depends on the unknown ToF at the next frame. | Motion row, no clear evidence of a >1.5x error; left alone |
| 2475/2481/2487 | v at 1.3 s (cm/s) | 93.4 / 93.4 / 71.9 | At the apex the vertical speed is ~0. The approach toward the camera is ~70-73 cm/s (stated ranges 1.557->1.4115 in 0.2 s, confirmed by the 1.10 width ratio), plus ~9 cm/s lateral, so physically ~72-75. Emulated forward and backward differences give 12-85. | Left alone. The renders disagree (93.4 against 71.9) although they share one label, but neither value is grossly off. |
| 2476/2482/2488 | a at 1.0 s | 980 | Free fall (released at frame ~21, bounce at 26.2), so physically g. The label from finite differences of noisy ToF cannot be determined. | Left alone |
| 2477/2483/2489 | a at 1.3 s | 980 | Free flight at the apex, so physically g. | Left alone |

## Result
No fixes for family 0028.
The max-height value of 25 is supported by three routes: the table plane, the rise time and the pixel rise (24.6-27.6).
The motion rows are within the plausible label range, and none shows clear evidence of a >1.5x error.
