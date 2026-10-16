# Lab audit: family 0033 (captured_0033 / 0033s / 0033x), 9 scored rows

All 9 rows ask for the ping-pong ball's speed at 0.5 s, 1.4 s and 1.5 s, once per render (o, s, x). The three renders share one label set.

**Verdict: no fix.** Every current value lies inside the range of my physical estimates. None is anywhere near 1.5x off.

Scripts are in `scripts/`, and frames and crops are in `frames/`.

## Setup facts (from the frames)
- **Event.** The girl tosses the ball up (arc 1, apex at orig frame 8.45) and it bounces on the far part of the table (bounce 1, orig ~15.5). It makes a second arc (apex at orig 20.3) and bounces again (bounce 2, orig ~25.5). It hops once, then rolls toward the camera from video frame 29 to 35. It leaves the near edge at about orig 36-37 and falls toward the camera and out of frame (video 38).
- **Frame timing.** The video has 49 frames at 24 fps. Frames were dropped between video frames 11->12 and 35->36 (the same pattern as family 0035).
  - Mapping: orig = video k for k <= 11, k+1 for 12-35, k+2 for 36 and later.
  - Evidence: arc 1 fits a parabola with rms 0.25-0.47 px when corrected for the drop, against 8.6 px without the correction. At 35->36, the Δv sequence is 8.9 / 82.4 / 64.6, so the middle step spans two frames.
- **Table.** I fitted lines to the table top in the x render (`corners.json`). With f = 711, rectification gives W/D = 0.816, which matches 60.3 wide by 76 deep (0.793). It is clearly not 76 wide (1.26).
  - The camera is only about 18.7 cm above the table top, with a pitch of about 1.5°.
  - The horizon is at v ≈ 341, from the vanishing point of the left and right edges (624, 340.6).
  - The near-edge range is about 78-81 cm and the far-edge range about 148-153 cm.
- **Stated depths disagree with geometry.** At t = 0.9, ToF says 1.457 m. Plane, shadow and gravity give Z ≈ 1.1-1.2 m for arc 2, and the ball size gives about 0.9 m. At t = 1.4, ToF says 0.738 m, against about 0.82-0.86 m from the plane and 0.6 m from size.
  - Ball sizes look inflated by about 1.2x (bloom on the white ball, and the SAM2 mask).
  - These conflicts are normal ToF and label noise on a small fast ball. They are not evidence of a wrong answer.

## Row verdicts
| qids | question | current | my estimate (routes) | verdict |
|---|---|---|---|---|
| 2555 / 2558 / 2561 | v at 0.5 s | 182.2 / 190.0 / 182.2 | 153-200 (see below) | OK, within label noise |
| 2556 / 2559 / 2562 | v at 1.4 s | 123.9 / 125.4 / 123.9 | 100-130 (see below) | OK |
| 2557 / 2560 / 2563 | v at 1.5 s | 154.4 / 156.1 / 154.4 | 150-170 (see below) | OK |

### v at 0.5 s: 153-200 cm/s
The ball is in free fall in arc 1, 0.16-0.20 s after the apex.

- **Physics.** Speed is g times the time since the apex: 153 cm/s at exactly 0.50 s, 159 for the forward difference over orig frames 12->13, and 198 for 13->14.
- **Image route.** The arc-1 gravity fit gives a = 10.4-10.7 px/frame², so Z ≈ 105 cm. A simulation shows that a depth drift over 30 cm/s would raise the fit rms above what I observe, so the motion is essentially vertical. Image steps of 42.5 and 54.2 px/frame give 157 and 200 cm/s.
- **Agreement.** The two routes agree to within 2%. The current 182-190 lies inside the range, which is consistent with the tuned small-ball correction. If the labels had placed arc 1 at the ToF-like 1.46 m, the label value would be about 218.

### v at 1.4 s: 100-130 cm/s
The ball is rolling toward the camera near the near edge (video frame 34 to 35).

- **Plane route.** Back-projecting onto the table plane with the ball centre 2 cm up gives 122 cm/s for the forward difference. Averages are 112 over frames 31->35 and 115 over 29->35.
- **Second route.** I took the direction of travel from the image line's vanishing point (dX/dZ = 0.326) and combined it with the u coordinates. This gives Z29/Z35 = 1.36, against 1.335 from the plane.
- **Scale.** With Z35 between 0.6 m (size) and 0.78 m (plane), the speed is about 95-125 cm/s.

### v at 1.5 s: 150-170 cm/s
The ball has just left the edge and is falling.

- The image step from orig 36 to 38 is about 48 px/frame. At Z ≈ 0.7 m that is about 122 cm/s in the image plane, plus about 100 cm/s in depth, so roughly 158 cm/s.
- The next step, orig 38 to 39, gives about 195 cm/s.

## Not changed
- All speed rows are leaderboard-tuned. None is grossly wrong (no wrong object, time, axis or segment), so none is touched.
- The 4% split between renders at 0.5 s (190 for s against 182 for o and x) is not worth touching.
