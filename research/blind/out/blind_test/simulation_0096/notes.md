# simulation_0096 (A2MX, 24 fps, 1920x1080, 41 frames)
Scene: uniform grey background, static camera. Cybertruck-like car (front at left) starts from rest and accelerates
leftward; Air China A320-like plane flies rightward at constant speed (exits frame ~25). Frames 0 and 1 identical.

## Scale from prior (car acceleration = 10 m/s^2)
- Car tracked per frame (bg-difference mask, centroid and 50%-contrast sub-pixel edges). Quadratic fit over frames 1-40:
  centroid 201.95 px/s^2 (resid 0.09 px), front edge 202.0, rear edge 199.2, edge midpoint 200.6. Constant acceleration.
- Perspective: car length grows 113.4 -> 116.6 px as it moves left (near/far corner effect, h/Z ~0.0066), plane
  near-engine moves 6% faster than the tail fin (Z ~100-150 m). The centroid is near-side dominated, so the origin
  acceleration is ~200.6-201.95 px/s^2 -> s = 0.0495-0.0499 m/px; used s = 0.0497.
- Sanity: plane length 759.6 px -> 37.6-37.9 m (A320 37.57 m); car 112.7 px -> 5.6 m (Cybertruck 5.68 m). The car and plane are at the same depth.

## Answers
- 169 plane speed at 0.3 s: tail-fin template (centreline) 50.474 px/frame, constant (std 0.05) -> 1211.4 px/s * 0.0497 = 60.2 m/s (high confidence, +-1%).
- 172 plane length: nose tip 1439.9 (50% crossing) - faint tail-cone tip 680.3 = 759.6 px -> 37.75 m (high).
- 173 plane height: fin top 284.1 to near-engine bottom 510.4 (226.2 px raw, +~1 px perspective for near engine) ~227 px -> 11.28 m (medium-high).
- 170 car length: 113.4 px in straddle regime / (1+h/Z) -> 112.7 px -> 5.60 m (medium-high).
- 171 car height: 37.5 px raw (roof peak to tyre bottom, 50% crossings), ~37.1 after near-wheel perspective -> 1.84 m (medium).
