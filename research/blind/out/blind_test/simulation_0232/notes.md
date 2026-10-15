# simulation_0232 notes
Scale: black cat walks on the teacher's table at 9.02 px/frame (bbox edges, 49 frames), so 216.5 px/s, giving 0.003298 m/px at the cat's depth.
Camera: ceiling-line vanishing point is at (960,539), so the camera is level and the horizon is at y=540.
Depths from floor and table-top rows:
- Wall/floor line y=951, wall/ceiling line y=172.
- Table top front y=766, back y~733: back/front depth ratio ~1.17, so the table back is about at the wall.
- Cat feet y=742: cat depth ~0.956 of the wall depth.
- Scales: wall 0.00345 m/px; table front 0.00295 m/px.

Answers:
- Ceiling: 779 px x 0.00345 = 2.69 m. If the cat is at the wall, 2.57 m. Answer 2.63. Medium confidence.
- Table length: front edge 72..779 = 707 px at front depth, about 2.08 m (1.99 m if the cat is at the wall). Answer 2.05. Medium confidence.
- Chair by the right wall (no blackboard visible): seat 163 px at the front-leg depth, about 0.48 m. Medium-low confidence.
- Clock: 114 px at the wall, 0.376-0.393 m. Answer 0.385. Medium confidence.
- Cat: bbox about 187 x 145 px at the cat scale, 0.62 x 0.48 m. Medium confidence.
- Paper airplane: tracked frames 13-36 (tail edge and centre y), local quadratic fits (+-3..5 frames), cat scale (depth unknown, assumed near the back plane).
  - Speed 5.41 m/s at 1 s and 4.84 m/s at 1.25 s.
  - Deceleration from local fits 2.7-3.2; mean over that interval 2.3.
  - Answers: acceleration 2.9 at 1 s and 2.7 at 1.25 s. Low-medium confidence, because the plane's depth is unknown.
