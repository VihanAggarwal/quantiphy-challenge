# simulation_0145 — HIMARS-like truck launching a rocket (S2MC, 24 fps, 29 frames, 1920x1080)

Static camera, side view of the truck. The rocket starts inside the launcher pod and first shows at frame 3. It is fully
out by about frame 13 and leaves the top-left of the frame between frames 22 and 25.
Prior: rocket length = 2.9 m (the only scale; 2D planar video).

## Scale
- Rocket path is a straight image line at 39.08 deg (perpendicular residual < 1 px). I resampled frames into strips along it.
- Body length: about 222 px from the cone tip (darkness > 120) to the base, where the bluish-white exhaust glow starts.
  A thin, faint nose spike adds about +14 px (measured in frames 15–18), so the full mesh is about 236–238 px. Without the spike it is about 226 px.
- Used L = 236 px, so k = 2.9/236 = 0.01229 m/px. The uncertainty is about ±3% (226 to 240 px).
- I checked for motion blur and found none worth counting: the rocket width (about 11.5 px at 50% contrast) does not shrink, and the body length does not grow with speed.

## Tire (qid 339)
- Silhouette widths at hub height: front 100.5 px, middle about 98.5 px, rear about 99.5 px, so about 99.5 px. The vertical extent is 96 px; the bottom is probably sunk into the ground or flattened, so I did not use it.
- Perspective: the near-side tires are about W/2 (about 1.4 m) closer to the camera than the rocket and pod plane at the truck centre.
  - I estimated the camera distance as D ≈ 60–70 m from the visible flatbed and cab-roof top surfaces (8.5 px and 5 px thick), assuming a level camera with the horizon at y≈540 and a truck width of about 2.5–2.9 m.
  - Factor ≈ 0.978.
- Diameter = 99.5 * 0.978 * k = 1.20 m (1.22 m without the perspective factor). Confidence: medium.

## Motion (qids 340–342)
- Displacements per frame come from NCC registration of the nose template in the rectified strip (frames 5–21; the nose is clear of the launcher arm from frame 9).
  - From frame 16 onward I also registered the tail template.
  - Tail shifts run about 0.5–0.9 px/frame above nose shifts, probably because the exhaust glow is growing. I corrected for that.
- Speed per frame rises from 16 px/frame (k=5) to 57.3 px/frame (k=21) and about 63 px/frame (k=22–24).
  - The acceleration clearly falls over time: a quadratic fit beats a linear one (rms 0.9 vs 1.4).
  - The data fit Blender Bezier ease-in (smoothstep) motion well: start t0 ≈ -0.5 frame (the rocket is at rest at video start), duration T ≈ 100–110 frames.
- Speed at t=1 s (frame 24, backward difference): model 64.3 px/frame, direct tail measurement 63.0–63.4. Used 63.9 px/frame
  → 1534 px/s → **18.85 m/s**. Confidence: medium-high, with scale uncertainty of about ±3–4%.
- Acceleration at t=1 s (second difference centred at frame 23): smoothstep and quadratic fits give 1.84–1.95 px/frame²; a constant-acceleration fit would give about 2.5.
  Used 1.9 px/frame² → 1094 px/s² → **13.45 m/s²**. Confidence: medium-low, because it depends on the model.
- Average speed from beginning to end: the model gives about 1155 px of displacement over frames 0–28. That is 41.3 px/frame over 28 intervals, or 39.9 if divided by 29 frames.
  Used 40.6 px/frame → **11.97 m/s**. Confidence: medium. It relies on the model during frames 0–3 (rocket inside the pod) and 25–28 (rocket out of view).

## Files
track*.py, reg*.py, edges.py, ends.py, fit*.py (measurement scripts); answers.json.
