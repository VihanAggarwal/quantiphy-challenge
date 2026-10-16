# 0031 independent re-measure (qid 2530 only)

qid 2530, captured_0031s: "velocity of the white ball at 1.6s (cm/s)". Current answer is 30.0.
The sibling renders of the same event are 2524 (captured_0031), currently 47.76, and 2535 (captured_0031x), currently 45.6.

I did not read anything else in research/next/labaudit/0031/. My scripts, frames and crops are in `0031/remeasure_2530/`.

## Video facts
- All 3 renders: 49 frames, 24 fps, 1280x720. They are frame-aligned: the white-ball centres agree to within 1 px per frame.
  t=1.6 s falls at frame 38.4. If the labels use a 25 fps time base, it falls at frame 40.
- The two balls rest at the back edge until about frame 14. Then both roll toward the camera.
  The tennis ball leaves the front edge at about frame 42-43. The white (ping-pong) ball is still rolling at frame 48.
- The s render's background and outline break edge fitting on the white ball. Measured on that render, the diameter reads 28-31 px and jumps around, which gives nonsense speeds of 9-16 cm/s.
  This is probably where the low per-render answer comes from. I measured on the original render (captured_0031); the labels are shared.

## Route 1: range from apparent size (f=711, D=4.0 cm)
- Sub-pixel radial-edge circle fit on each frame (`circfit.py`), checked by eye in `overlay_white.png`.
  The diameter grows from 21.2 px (frame 30) through 24.4 px (frame 38) to 29.0 px (frame 48).
- Range: R = r / sin(atan(rho/f)). Each point is P = R * ray(cx, cy). The speed comes from the derivative of polynomial fits.
- Speed at t=1.6 s: 46.2 (deg 2, frames 26-48), 48.3 (deg 3, 26-48), 47.5 / 43.7 (frames 30-48), 45.9 / 41.8 (frames 32-46). Median is about 46.
- The velocity is almost all along the line of sight (vz about -46, vx about -8, vy about 0).

## Route 2: table-plane geometry (independent of ball size)
- Table-top corners come from the x-render mask edges and the front crease (`table.py`).
  solvePnP with K (f=711) fits 60.3 wide x 76.0 deep (reprojection 4 px). The 76 x 60.3 orientation fits worse (18 px).
  The camera sits about 15.7 cm above the table top and about 85 cm in front of the front edge.
- Route 2b, homography only (no K): the bottom of the ball silhouette, about the contact point, mapped to table cm.
  The ball goes from y=45.5 cm (frame 30) to 28.2 (frame 38) to 10.5 (frame 48), with about 1 cm of lateral drift.
  Speed at 1.6 s is 46.5-48.7 cm/s. As plain chords: frames 36->40 give 46.2, 34->42 give 48.9, 30->48 give 46.7.
- Route 2a, ray through the ball centre meeting the plane z=2 cm, with pose from K at f=690/711/730: 46.0-48.4 cm/s. This hardly depends on f.

## Result
The white ball's physical speed at t=1.6 s is **46.5 cm/s**, likely range 44-49. On a 25 fps label time base (frame 40, dt=1/25) it would be about 48.
The current 30.0 is a factor of 1.55 too low, so it meets the ">1.5x off" threshold. It also disagrees with the sibling renders that share the same labels (47.76, 45.6).
Recommendation: give 2530 the same answer as 2524 and 2535, with the same noise policy.

## Flag: depth_info names are swapped in this event
depth_info gives white ball = 0.994 m and tennis ball = 1.190 m at 1.6 s. Image measurements show the reverse.
- At frame 38 the white ball's centre range is 116.7 cm (size route) and 113.4 cm (pose route). Its front surface is about 1.14 m.
- At frame 38 the tennis ball (49.0 px, 6.7 cm) has a centre range of 97.2 cm, and a front surface of about 0.94 m.
- The white/tennis range ratio is 1.20 in the image. The stated ratio is 0.835, and swapping the names gives 1.197.
  No choice of f or time offset fits the unswapped values: they are wrong by -12% and +29%, in opposite directions.

So the object stored as "white_ball" has the tennis ball's depth at 1.6 s. If the stored tracks themselves are swapped, not just the depth text, the velocity label for "white ball" would be the tennis ball's speed.
The tennis ball's physical speed at 1.6 s is about 60-67 cm/s by both routes. That number depends on the fit window, because the ball reaches the front edge around frames 40-42.
I cannot tell from the inputs whether the swap reaches the velocity tracks. My primary answer is the physical white-ball speed.
