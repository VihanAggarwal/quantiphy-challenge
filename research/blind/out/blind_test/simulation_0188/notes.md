# simulation_0188 — catering truck (MAN cab + box + roof platform) accelerating left->right, static camera

## Camera / scale
- Static camera (frame 0 vs 59 differ only on the truck). Verticals exactly vertical -> pitch ~0, horizon y~538.
- VP1 (hangar wall horizontals, 66 LSD lines, RANSAC) = (-3138, 537); truck box edges give the same VP -> truck moves parallel to back wall.
- VP2 from ~30 truck front-face horizontal lines (frames 0-30) clusters at x~2715 -> f = sqrt((2715-960)(960+3138)) = 2682 px (HFOV ~39 deg).
- Front-hub rim tracked (bright-rim blob + ellipse fit) frames 0-46; fitted 3D straight-line constant-acceleration model
  s=0.5*a*(t-t0)^2 with a=10.757 (prior): rms 0.2 px, t0=-0.001 s (starts from rest at t=0). Metric scale comes from a.
- Cross-check with depth_info (Euclidean range to AABB centre): predicted 22.53/19.49 m at f=2690 vs given 22.532/19.525 -> f=2690 (+-20)
  agrees with VP route (2682); rim-ellipse aspect route gives 2670-2780. Sizes are nearly f-independent (scale from kinematics).

## Truck geometry (truck frame: l along travel from front hub, w lateral from near rim face, h above ground)
- Camera height 2.32 m; tire radius from hub->ground contact (19 frames): 0.394 (+-0.003); near-edge correction -> ~0.387. Diameter ~0.78.
- Rear box edge (silhouette triangulated over frames 36-47, rms 0.2 px): l=-6.912, w=-0.114. Underride bar l=-6.85 (not behind box).
- Front: grille logo/plate/headlights l=1.14-1.17; cab far corner l=1.09; platform front roller (silhouette at h~2.4) l~1.30.
  Length = 1.30 + 6.91 = 8.21 m.
- Height: topmost silhouette point (roof-platform rail, triangulated l=0.36, w=-0.07) h=3.41 m (ground = tire contact).
- Centreline w=1.02 (MAN logo / plate triangulation). Box width = 2*(1.02+0.114) = 2.27 m. Mirrors: far mirror outer w~2.31
  (silhouette, h 1.6-2.1), near mirror housing centre w=-0.25 -> mirror span ~2.6 m.
- Wheels do not rotate (rigid model translated) -> AABB likely includes mirrors; answered a hedge 2.55 (between 2.27 body and ~2.61 mirrors).

## Speeds
- Constant acceleration from rest at t=0: v=a*t -> 10.757 / 16.136; backward-difference convention gives 10.59 / 15.97.
  Answered midpoints 10.67 / 16.05 (within 1% of both).

## Answers / confidence
- 1439 length 8.2 m (high-medium; front-most part ambiguity +-0.07)
- 1440 height 3.41 m (high)
- 1441 tire diameter 0.78 m (high)
- 1442 speed@1s 10.67 m/s (high)
- 1443 speed@1.5s 16.05 m/s (high)
- 1444 width 2.55 m (low-medium: body 2.27 vs incl. mirrors ~2.6)
