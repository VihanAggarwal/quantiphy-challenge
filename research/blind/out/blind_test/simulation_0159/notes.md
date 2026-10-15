# simulation_0159 (A3MS, 24 fps, 41 frames, 1920x1080) - shark + leatherback turtle, static camera

## Tracking
- Background = masked temporal median (mkbg.py); masks by |frame-bg| > 25 (seg4.py, overlays checked).
- Turtle: frame-to-frame chained template tracking of the carapace (chain.py -> chain_turtle_A.json; alt templates B, C).
- Shark: dorsal-fin tip (topmost mask point, feats.py), head/dorsal template chain (chain2.py), extreme points (feats2.py).

## Geometry / camera
- 3D model per object: origin(t) = O0 + h*(v0 t + a t^2/2), straight line, pinhole, principal point at centre.
- Depth convention: Euclidean RANGE fits (predicted R(0.5) matches for both objects); optical-axis Z convention
  predicts Z(0.5) independent of f and misses both givens (turtle 15.014 vs 14.968, shark 15.876 vs 15.744) -> rejected.
- Focal length: (1) turtle acceleration prior 2.639 -> f ~ 2575-2620 (carapace tracks A, C, A+C; B with flipper root 2400);
  (2) shark R(0.5)/R(0)=0.95569 with origin = 3D bbox centre -> f ~ 2620-2690 (fin track), 2860 (fin+template).
  Adopted f = 2650 px (~43 deg HFOV, close to Blender 50 mm default 2667).
- Both animals start from rest (v0 ~ 0) with constant acceleration (jerk term ~0 on cleanest tracks), same heading
  (yaw ~ -141 deg in camera xz, i.e. ~40 deg toward camera from the image plane), horizontal (pitch ~0 -> camera level).

## Answers
- Turtle speeds: v = a (t - 1/48) with a = 2.639 (backward difference): 2.584 @1s, 3.903 @1.5s. High confidence.
- Shark (f=2650, fin track, origin at 3D bbox centre 0.19 m behind / 0.66 m below fin tip): a = 6.82, v0 = 0.035;
  speed 6.71 @1s, 10.12 @1.5s. Medium-high confidence (f uncertainty +-150 px -> +-2-3%).
- Shark length: nose / caudal-tip intersected with the body mid-plane, frames 20-37 median: 4.41 m (minus ~0.05 snout
  silhouette bias) -> 4.38 m. Medium confidence.
- Turtle length: along-heading extent head (~0.99-1.07 m ahead of carapace centre) to rear (carapace tip -0.6 m,
  rear flipper tip -0.65..-0.95 m depending on its lateral offset) -> 1.65-2.0 m; answer 1.85 m. Low-medium confidence
  (definition of AABB 'length' with flapping flippers; front-flipper span ~1.9 m).
- Water-depth difference: camera level; shark centre Y = -1.30 m (above axis), turtle centre Y = +0.80 m (template centre
  0.776 + small offset) -> 2.10; with flippers in turtle AABB ~2.2; answer 2.13 m. Medium confidence.
