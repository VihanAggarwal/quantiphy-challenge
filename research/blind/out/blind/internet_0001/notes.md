# internet_0001 - top-down drone view of a 6-lane highway, black SUV moving left to right in lane L4-L5

Video: 3840x2160, 31 frames, dataset fps 24 (the container reports 20.62 fps; I used the dataset value of 24).
The camera is static (phase-correlation drift under 2 px). Background = median of the frames.

## Scale (prior: lane width = 3.66 m)
- Dashed lane-line centres, from connected components of the background, at x~2000: y = 358, 665, 989, 1307, 1613, 1945.
- The black car drives in the L4-L5 lane, which is 305.3 px centre to centre (303.7 at x~700, 306 at x~3100).
  The mean lane is 317 px; lane widths differ from 305 to 331 px.
- I used an effective lane width of 308 px, weighted toward the car's own lane: 0.01188 m/px.

## Car measurement (ratio image frame/background; the shadow is ~0.7, car body ~0.45, road ~0.92)
- Edges were measured per frame at the 50% crossings, in rows relative to the car. The rear edge uses the bottom
  rows, where road rather than shadow is behind the car.
- Length (50% points) is 422-436 px; the minimum is near the image centre and it grows toward the edges, from
  parallax and a slight pincushion effect (dashes are 2.5% longer at the edges). Frame 12 detailed profile: 434-437 px.
  The visible extent including the motion-blur fringe is about 450 px. Motion blur is about 25 px (from a
  specular streak).
- Used 440 px, which gives a length of 5.23 m.
- Width (top edge against the shadow, bottom edge against the road, mirrors excluded): 188-191 px. Used 189 px,
  which gives 2.25 m. Physically this is likely about 4% high because the car side is visible at 390 px below centre.
- Speed: linear fit of the mid-point between the front and rear edges over frames 0-22 gives 121.7 px/frame
  (rms 2.6 px). Vertical drift is 1.6 px/frame. 121.7 x 24 x 0.01188 = 34.7 m/s.
  With the 305 px lane it would be 35.0; with 317 px, 33.7; with the container fps, 30.

## Confidence
- 2151 length 5.23 m: medium. Depends on the blur convention (434-450 px) and the lane choice.
- 2152 width 2.25 m: medium.
- 2153 speed 34.7 m/s: medium-high if 24 fps is the convention used for the ground truth.
