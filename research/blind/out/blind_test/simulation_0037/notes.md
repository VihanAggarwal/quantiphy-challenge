# simulation_0037 — notes

Question 1153: height of the person (m). Prior: speed of the person = 1.3 m/s. Depth to pelvis 122.857 m (t=1 s) and 122.859 m (t=2 s), so the range stays constant: the walk is tangential to the line of sight (closest approach near t≈1.4 s), and one m/px scale applies to both the motion and the body height.

## Method
- Static camera: frame-to-frame differences outside the person are about 0. Background = median over the frames; the person is segmented by background difference (scripts in work/).
- Horizontal track (upper body, head and full-mask centroids, linear fit over 72 frames): 41.36 / 41.38 / 41.22 px/s. Vertical drift is about 2.3 px/s, so the 2D image speed is 41.42 px/s. The speed is constant (quadratic term is negligible).
- Cross-check: stance-foot positions are about 29.5 px apart, the cadence is 1.43 steps/s (period of the leg-spread signal 16.75 frames), and 29.5×1.43 = 42 px/s. The feet do not slide.
- Scale: 1.3 / 41.42 = 0.03139 m/px. Off-axis correction (person about 4.7° off-axis, f≈3900 px) is about 1.003.
- Pixel height (blurred/anonymised head top to shoe sole, excluding the wet-sand reflection under the feet):
  - per-frame half-max edges: median 61.0 px; linear fits of top and bottom at t=1.5 s give 61.1 px
  - drift-aligned averaged profiles: 60.3–61.7 px, depending on the edge levels
  - visual reading of mid-stance frames: f1 ≈64, f34 ≈61.5, f68 ≈61.5 px
  - a cruder threshold method that includes part of the reflection gives 64.5 px (upper bound)
  - Adopted: 62 px, a little above the mean walking-pose height (rest or upright stature is about 1–2% taller).
- Height = 62 × 0.03139 × 1.003 ≈ 1.95 m (range 1.92–2.02 m for 61–64 px). Implied f ≈ 3900 px (hFOV ≈ 16°), which is plausible.

## Confidence
Medium. The main uncertainty is the head top (the face/head is blurred, ±1.5 px) and the contact line with the reflection (±1 px). Expected error is about 3–4%.
