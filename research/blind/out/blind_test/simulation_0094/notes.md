# simulation_0094 (V2MX, 24 fps, 1920x1080, 38 frames)
Scene: white Cybertruck-like car moving right (y~631-673) and an Air China A320 moving left above it, on a flat grey background. Frame 0 is the empty background, which gives clean background subtraction.

## Scale (prior: car speed = 30 m/s)
- Tracked car edges with subpixel accuracy over frames 11-37. Rear edge 28.530 px/frame, front edge 28.26 px/frame, bbox centre 28.394 px/frame (constant speed).
- The two edges move at different speeds because of perspective: the near-rear and far-front corners sit at different depths. Their average gives the origin's pixel speed.
- s = 30 / (24 * 28.394) = 0.044024 m/px at the car's depth.
- Plane speed: 56.75 px/frame * s * 24 = 59.96 m/s, which is exactly 2x the car's speed. Its length at the same scale is 37.57 m, the real A320 length. Both strongly suggest the plane is in the same plane (same depth) as the car, so one scale is used for both.

## Perspective checks
- Car extent shrinks linearly as it nears the image centre (front face visibility; slope -0.0095 px/px). I extrapolated the extent to x = 960, which gives f*L/Z = 126.5 px (half-contrast threshold).
- The plane's near horizontal-stabiliser tip moves 4.6% faster than the nose or tail (d/Z ~ 0.044). The near wingtip also moves faster (b/Z ~ 0.12). These are consistent with A320 proportions and with f ~ 3200 px (FOV ~33 deg).
- Horizon / pitch: the far-side tyres peek out right of the near tyres in early frames (dx ~12 px, dy ~1.8 px), which puts the horizon at y ~ 537 (camera roughly level). The windshield band alone suggested a higher horizon (~390). I treated it as model geometry, since the tyre cue is cleaner.

## Answers
- 160 car length: 126.5 px * s = 5.57 m (threshold spread 5.54-5.61). Confidence: high.
- 161 car height: silhouette 630.64 to 672.94 = 42.3 px, minus ~1.5 px for the near-tyre and roof-top perspective. 40.8 px * s = 1.80 m (range 1.77-1.86 depending on the horizon). Confidence: medium-high.
- 162 plane length: nose to tail cone, 853.4 px (frames 31-37, where both ends are on the centreline) = 37.57 m. The stabiliser tip sits ~0.9 m forward of the tail cone, so the tail cone is the bbox end. Confidence: high, given the same-depth assumption.
- 163 plane height: fin tip 300.3 to nacelle bottom 553.7 = 253.4 px, minus ~0.7 px because the near engine is closer to the camera. 252.7 px * s = 11.12 m (range 10.9-11.2). Confidence: medium-high.

Scripts are in work/ (seg.py, edges.py, carv.py, plane.py, planeprof.py, band*.py, bottom.py).
