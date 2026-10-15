# internet_0055 notes
- 2.5 s handheld clip (75 frames, 1920x1080). Small camera drift (~10 px right, ~15 px down). No scaling/zoom (sign pixel sizes constant).
- PRIOR UNUSABLE: prior is speed of a "person riding scooter" but no scooter rider appears in any frame (checked montage of frames 6..66). Only a walking woman.
  Using the walker as the 1.95 m/s object would imply height ~2.1 m (implausible), so scale was taken from real-world geometry instead.
- Ground-plane model: horizon y~440 (t0) from parked Tesla (top 437/bottom 497, 1.62 m) and Marguerite bus (roof 320/wheels 545, ~3.1 m) -> camera height ~1.5 m (both agree).
- Walker: 262 px tall, feet y 686 (t0); 314 px, feet 730 (t2.4, horizon ~452) -> H = 1.60 / 1.69 -> 1.63 m.
- Bicycle diamond: bbox 162x167 px, pole base y~660 -> 147 px/m -> 1.10 x 1.14 m bbox = standard 30" W11-1 diamond (bbox 1.078 m). Diamond bottom y 275 -> 2.6 m above ground (plaque bottom would be 2.14 m).
- DO NOT ENTER: 151x150 px; pole base hidden behind bushes whose front edge is y~700 -> size >= 0.87 m -> 36" R5-1 (0.914 m), base ~y688, bottom edge 2.3-2.5 m above ground.
- YIELD: 122 px wide, plaque 85 px; ratio favours 36" (0.914 m).
Confidence: walker height medium; sign sizes medium (standard-size assumption, bike bbox vs side ambiguity); heights above ground low-medium.
