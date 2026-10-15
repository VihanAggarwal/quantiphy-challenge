# simulation_0033 - measurement notes

## What the scene shows
- A fixed 1080x1080 camera at 30 fps, 54 frames, facing a white brick wall.
- An orange Kia-Stinger-like car drives right to left in the lane next to the curb and slows down. The prior gives its acceleration as -2.86 m/s^2.
- A grey/green car crosses fast in the near lane during frames ~22-38.
- A person walks right behind the hydrant and the lamp post.

## Camera
- Depth convention: the distances are Euclidean range to the object origin. The orange car keeps a constant pixel size while d(0)=12.048 and d(1)=10.432, so the distance cannot be optical-axis Z.
- Pitch: the lamp post and the wall pilasters converge to a vertical vanishing point at y ~ -25000. That means the camera is pitched up about 3.4 deg, so the horizon sits at y ~ 450. Roll is about 0.
- Focal length f ~ 1495 px (HFOV ~ 39.7 deg), found as follows:
  - The roof shark-fin antenna lies on the car's centre plane. Its centroid track over frames 18-53 gives a pixel acceleration of 423 px/s^2.
    - Tracking the near-side panel instead gives 465 px/s^2. The ratio 0.927 is the parallax between the side panel and the centre plane.
    - Scale at the car-centre depth: s_c = 2.86/423 = 0.00676 m/px.
  - Independent route: X0^2 - X1^2 = d0^2 - d1^2, using the bbox-centre pixel track, gives s_c = 0.00680. The two routes agree.
  - f = sqrt((d1/s_c)^2 - r^2): 1504 for a body-centre origin, 1478 for a ground origin. The car far side not intersecting the curb also needs f <= ~1510.
- Consistency checks:
  - With the hydrant and lamp origins at their bases, both bases and the person's feet fall on one plane, Y = -2.04 m (the sidewalk).
  - The orange car comes out at 5.0 m long, which fits a real Stinger with the scene at about real scale.

## Answers (f = 1495, pitch 3.4 deg; heights from 3D back-projection onto each object's vertical axis)
| qid | quantity | answer | basis | confidence |
|---|---|---|---|---|
| 1134 | person height | 1.87 m | head top 649.8 to feet 864.5 px at pelvis depth (d = 13.78) | medium-high |
| 1132 | hydrant height | 1.03 m | cap top 755 to base, origin at base (d = 12.565) | medium-high |
| 1133 | streetlight height | 4.44 m | finial 327.5 to base 891 (d = 12.325) | medium-high |
| 1136 | orange car length | 4.97 m | front tip crosses the image centre at frame 16, rear at frame 53; centre-plane displacement in between from the antenna track x s_c | medium |
| 1137 | orange car height | 1.48 m | antenna tip at y=741 (centre depth) down to road level from the tyre bottom (~997 px) and the curb; the bare roof would give ~1.45 | medium |
| 1138 | curb height | 0.22 m | curb face 907.5-936 px (0.21); tyre-contact road level gives 0.21-0.27 | low-medium |
| 1131 | person walking speed at 1 s | 0.50 m/s | smooth lateral pixel velocity at t=1 is 58.5 px/s, x z_c/f (13.15/1495) = 0.515; locally the step cycle is near mid-stance (head/torso about 1.5 px/frame, ~0.41 m/s); I leaned toward the smooth value because the feet appear to slide (in-place walk cycle plus object translation) | medium-low |
| 1135 | green car speed at 1 s | 11.9 m/s | with constant velocity, X0 = sqrt(d0^2 - d1^2 + X1^2) and X1 = 0.1-0.5 m, giving 11.7-12.2; the pixel route (cabin moves 127-137 px/frame at depth 4.2-4.8 m) gives 11.6-12.2 | medium |

## Scripts
- otrack5.py, solvepos.py, velfit.py: orange car track.
- ant2.py, antfit.py: antenna track.
- cam.py, sizes.py, carh.py, curb2.py: camera model and object sizes.
- ptrack.py, pfit.py, pvel.py: person track.
- gres.py, gtm.py: green car.
