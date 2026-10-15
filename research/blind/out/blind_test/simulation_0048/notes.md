# simulation_0048 - notes

## Scene
Static camera (frame-diff ~1 grey level), 1920x766, 33 fps, 99 frames. Street seen from a raised viewpoint looking down
(camera above the road, ~0.8 m right of the curb). Walker on the right sidewalk and cyclist on the road both approach the
camera along the street. Grey kiosk / "telephone booth" in the foreground. Victorian facade with doors on the right.

## Camera (pinhole, principal point at image centre)
- Vertical vanishing point from 51 RANSAC inlier vertical edges: (~945, ~7800).
- Along-street VP from two fitted curb edges: (1770, -71). Across-street VP from booth edges + far road edge: (~-3535, -66).
  The horizon is at y ~ -70 and roll ~ 0. The VP triangle's orthocentre is (~946, 398), close to the image centre.
- f: VP orthogonality 1834-1864; booth-top VP 1735; manhole ellipse normal 1690; bike constant speed 1780; walker
  height constant along its path ~1850. Used f = 1830 px (HFOV ~55 deg), pitch = atan(f/7412) = 13.9 deg.
- The booth cap reconstructs as a square with an 88 deg corner. The bike motion direction matches the street VP direction.

## Scale
- Walker head top and feet in many frames: height = 0.390-0.396 x (camera height above sidewalk) at f = 1830.
  The 1.8 m prior gives Hs ~ 4.55-4.62 m.
- depth_info for the HUMAN (11.93 / 10.82 m) is inconsistent with the image: a 1.8 m walker would be ~17 m away,
  and the walker's feet are higher in the image than the bike's contact point while the label says the walker is
  closer. These labels were not used for scale.
- depth_info for the BIKE (16.49 / 11.93 m) fits the geometry with road camera height Hr ~ 4.8 m
  (origin ~1 m behind the front contact), within ~3% of the prior scale (with a ~0.12 m curb).
- Used Hs = 4.62 m and Hr = 4.74 m.

## Answers
- 1195 bike speed: ground track of the front-wheel contact for frames 0-58 gives a constant 1.000 Hr/s, so
  4.67-4.74 m/s from the prior scale and ~4.8 from the bike labels (the label range rate of 4.56 m/s also matches).
  Answer 4.75. Confidence: medium-high.
- 1191 walker speed: planted-foot positions and the head track in the head plane, over whole gait cycles, give
  1.09-1.19 m/s. The walker-label range rate of 1.11 m/s implies ~1.14 m/s. Answer 1.13 (t=1 is mid-stance).
  Confidence: medium.
- 1194 bike height: handlebar top, assumed 0.25-0.45 m behind the front contact, reconstructs at 0.92-0.98 m
  consistently in frames 20/33/50. Answer 0.95. Confidence: medium.
- 1196 wheel diameter: front wheel vertical extent (bottom to lamp/fender) in frames 20/33/50 gives 0.65-0.71 m.
  Answer 0.69. Confidence: medium-low.
- 1192 booth width: the cap is square, w = 0.695 x (Hs - z_top). The booth base is below the frame, so the
  back-right edge only gives z_top >= ~2.42 m, hence w <= 1.52 m. Assumed a typical height of 2.5-2.6 m:
  answer 1.42. Confidence: low-medium.
- 1193 pillar distance: facade plane at lateral -3.75 m (the building corner meets the side-wall base line at s = 11.8;
  this agrees with the stoop railing top end at -3.7). Near door A, left pillar centre x~1190;
  far door B (twin door under the second lintel), right pillar centre x~1310. Centre-to-centre is ~3.8-3.95 m.
  Answer 3.9. If the "far door" were the dark porch further right, the answer would be ~7.4.
  Confidence: low-medium.
