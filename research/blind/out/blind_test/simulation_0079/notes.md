# simulation_0079 — notes

Scene: straight-down (nadir) fixed Blender camera, 1920x1080, 24 fps, 72 frames (frame 0 duplicates frame 1).
A cyclist on a cyan bike (y~650) and a walker in a white shirt (y~435) both move toward -x.
Prior: the bike is 1.7 m long (bounding box, so tire tip to rear-fender tip).

## Measurements (scripts/)
- bike.py, bikefit.py, tipprof.py: sub-pixel front and rear tips of the bike from chroma and luma edges.
  - Front tip moves 51.087 px/frame and rear tip 51.382 px/frame, both linear (rms 0.5 px, no acceleration).
  - The pixel length shrinks 0.295 px/frame, which matches the tip-speed difference exactly. So this is
    parallax from a small height difference between the tips; no camera tilt is needed.
  - Length with the front tip at the principal point is 412.35 px, so s_rear = 242.56 px/m and s_front = 241.17 px/m.
- head.py: walker hair blob centroid (smooth track). shoes.py: shoe blobs.
  shirt.py: centroid of the white shirt. rider.py: rider head by template matching.
- Camera height from parallax (H ~ 20 m, f ~ 4740 px, HFOV ~ 23 deg):
  - The walker's head moves 1.09x more pixels per stride than his feet. With head height ~1.7 m, H ~ 19-20 m.
  - The rider's head drifts relative to the bike tip at slope 0.069. A ~1.6 m head height gives H ~ 20 m.
  - The head drifts against the shirt centroid; this is consistent with the shirt centroid at h ~ 1.23 m.
- The stance feet slide forward about 4 px/frame. This points to an in-place walk cycle plus a constant
  translation, so the pelvis moves at a nearly constant velocity.

## Answers
- Q77 bike speed: 0.85*24*(51.087+51.382)/412.35 = 5.08 m/s. This does not depend on H; the bike moves
  at constant speed. Confidence high.
- Q76 walker speed at 1.0 s:
  - Mean head velocity is 14.40 px/frame. Head-height scale is 259 px/m (H=20, h=1.7), giving 1.335 m/s.
  - Footprint route: 13.1-13.2 px/frame at ground scale 238 px/m gives 1.33 m/s.
  - Head instantaneous velocity at frame 24 (backward diff) is 0.97x the mean, giving 1.30.
  - Answer 1.32. Confidence medium-high.
- Q78/Q79 distances:
  - Pelvis is taken 0.07 m behind the head along the walking direction, at h ~ 1.0 m.
  - Bike origin is the bbox centre: the midpoint of the tips, h ~ 0.5 m, so dz ~ 0.5.
  - Horizontal distance is 3.82 m at frame 24 and 2.07 m at frame 12.
  - 3D distance is 3.86 m (f24), 3.93 m (f24.5), 4.00 m (f25); 2.13 m (f12), 2.20 m (f12.5), 2.27 m (f13).
  - Frame 0 is duplicated, so t -> frame mapping is uncertain (24 vs 25). I hedged slightly toward the half frame.
  - Answers 3.90 and 2.19. Confidence medium; the bike origin height and convention add the most risk.
