# simulation_0070 (S2MS, 2160x1080, 24 fps, 72 frames)
Top-down (nadir) Blender view of an intersection. Yellow car starts heading up (vertical) and turns right; by about 2.2 s it is horizontal.
A bicycle with rider travels straight up the road at x~918. Frame 0 is a duplicate of frame 1, and both objects move at constant speed after that.

## Scale
- Median background, then sub-pixel luminance edge crossings (175 = halfway between the shadowed road and the car body).
- Car length along its axis (centre band) = 217.7 +- 0.2 px in every frame 0-71 (it holds through the turn).
- So 5.44 m / 217.7 px = 0.02499 m/px.
- Perspective: lamp poles lean radially, so the camera is a true perspective camera. Estimated camera height is about 55-100 m, so height effects are about 1% or less. To avoid them, tracks use outline/end points at a similar height to the car outline.

## Q42 width
- Max per-column width (rear fender) = 79.4-80.0 px over frames 0, 2, 66 and 71. Width/length ratio = 0.365-0.367.
- Width = 1.99 m. No mirrors are visible in the top view.
- Confidence: high. Unseen mirrors would add a few %.

## Q41 car speed at 2.5 s (frame 60)
- Midpoint of the front and rear outline edges along the car axis: about 6.80 px/frame (linear fit over frames 55-65 = 6.80; frames 50-71 = 6.78).
- 6.795 * 24 * 0.02499 = 4.08 m/s.
- Cross-check: ECC rigid template gives 6.87 px/frame (4.12 m/s). It reads slightly high because it is dominated by roof-height texture under perspective.
- Confidence: high.

## Q43 bicycle speed at 1.0 s (frame 24)
- Sub-pixel front and rear end edges move 8.89 px/frame, constant over frames 1-71 (rms of residuals < 1 px).
- 8.89 * 24 * 0.02499 = 5.33 m/s.
- Cross-check: template match (rider-dominated) gives 8.975 px/frame (5.38 m/s). It reads slightly high because the rider sits higher.
- Confidence: high.
