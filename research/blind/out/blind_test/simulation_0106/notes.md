# simulation_0106 - two viruses separating (left goes up, right goes down)

## Observations
- 72 frames at 24 fps, 1920x1080, static camera, plain grey background. Frames 0 and 1 are identical, so motion starts after frame 1.
- Neither virus rotates. Both translate along image-vertical lines that converge to a vanishing point near (959, ~8150).
  As the left virus rises it grows (radius 122.7 -> 129.9 px over 35 frames). As the right virus falls it shrinks (137.7 -> 133.3 px over 25 frames).
  So the motion has a depth component: about 20 deg of tilt relative to the image plane (camera pitched down, vertical motion).
- Tracks come from a body-sphere circle fit (morphological opening with a 51 px disk, then a robust least-squares circle) in every frame.
  This gives the centre (taken as the origin) and the radius. Template matching gave a cross-check.

## Camera
- Focal length comes from the apparent rotation of spike tips caused by the change in viewing direction. About 25 red tips per virus were tracked.
  I fitted a 3D model of the tips (all tips at a common radius from the centre, front and back signs set) with exact perspective.
  Results: f = 2755 px (left) and 2851 px (right), RMS 0.9-1.1 px. Near-frontal tips alone give about 2400-2700. I used f of about 2780 (FOV about 38 deg).
- The answers barely depend on f: changing f from 2500 to 3000 moves the distances by less than 1.3%.

## Kinematics
- A joint projective constant-velocity fit (shared vanishing point; per-virus p0, r0 and relative depth rate a) has RMS 0.3 px.
  Speed is constant over frames 1-50, so the motion is linear with no easing.
- |a_L/a_R| = 0.993-0.999 across fit variants. The two viruses therefore change depth at the same relative rate.
  Their pixel speeds at the start are also equal (11.6 px/frame each).
  The consistent reading is scenario B: both start at the same depth and move at the same 3D speed.
  The right virus is then about 11-12% larger physically. Body radius is 0.657 m (left) and 0.732 m (right), at a depth of about 14.2 m.
  Under B the spike spheres of the two viruses just touch at t=0, which is consistent.
- Scenario A (identical sizes, right virus closer) would make V_L = 1.746 m/s and d(1s) = 4.51 m, d(2s) = 7.13 m.
  It needs a coincidence (speed ratio equal to depth ratio to within 0.7%), so I treat it as unlikely.

## Answers
- Q215, left virus speed at 1.0 s: B gives 1.5667 m/s (1.54-1.57 depending on variant); A gives 1.746. I answered **1.60**.
  This is a hedge: it is within 4% of every B variant and within 8.5% of A.
  Confidence: moderate-high (about 85% that B holds).
- Q216, distance at 1.0 s (frame 24, origins = body centres): 4.34 m (B) or 4.51 m (A). I answered **4.37**.
  Moving the frame by one changes it by ±0.10 m. Confidence: high.
- Q217, distance at 2.0 s (frame 48): 7.04 m (B) or 7.12 m (A). I answered **7.06**.
  Moving the frame by one changes it by ±0.12 m. Confidence: high.

Scripts are in work/: track.py, tm2.py, body2.py, tips.py, tipfit2.py, projfit.py, answers.py, final.py.
