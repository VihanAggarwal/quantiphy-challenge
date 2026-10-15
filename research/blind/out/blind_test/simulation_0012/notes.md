# simulation_0012: notes

The camera is fixed and looks straight down. A crow or raven flies left to right (+x) across a lawn below a wooden cabin with a gable roof and crossed bargeboards. The video is 1920x1954 and has 61 frames. The container runs at 22.93 fps, but the dataset runs at 24 fps, so the clip is about 64 original frames. Two frames are visibly dropped, at mp4 frames 18->19 and 42->43, where the step size doubles. I corrected for those drops when computing speeds.

Prior: speed of the bird = 6 m/s (no time given).

## Bird track (median-background subtraction plus template matching of head and body)
- The bird's speed in pixels is NOT constant. It follows an almost perfect parabola: 6.9 px/frame at the start, a peak of about 20.9 px/frame at original frame 30, and about 6 px/frame at the end. Fit rms is 0.3 px/frame, and the roots fall at original frames -6 and 66. This is a 72-frame (3.0 s) Blender Bezier ease-in/ease-out.
- Candidate pixel speeds for "6 m/s":
  - Average over the keyframe interval (designed distance/time): 2/3 of the peak, 13.9 px/frame.
  - Mean over the clip: 15.3-15.5.
  - Instantaneous at t = 0.5 s or 2.0 s: about 16.
  - Instantaneous at t = 1-1.5 s, or the peak: 20.3-20.9.
- I chose v = 15.4 px/frame (369.6 px/s) as the value with the lowest expected error. Bird-depth scale s_b = 6/369.6 = 0.01623 m/px.

## Depth: bird vs ground vs eaves (shadow parallax)
- The bird's and its shadow's tail and beak tips were tracked over frames 25-41. Bird speed / shadow speed = k = 1.249, so h_bird/H = 0.20. The sun offset at the bird's height is about (-64, +57) ground pixels.
- Two vertical structures (a fence post and a house corner post) both point back to a nadir near the image centre, (995, 965), which confirms the camera looks straight down.
- The house's shadow boundary on the lawn was modelled with the same sun vector:
  - Bargeboard tips cast shadows at a = 1.1-1.25 times the bird's height, giving h_eave ≈ 0.235 H.
  - The apex sits at about 2.4-2.6 times the bird's height, about 0.49 H. This agrees with the image parallax of the apex relative to the eaves, (H-h_e)/(H-h_r) ≈ 1.51.
- Eave-to-bird scale factor: (1-0.235)/(1-0.1995) = 0.956.

## Measurements
- House, eave to eave (bargeboard tip to tip): x 396.5 to 1389 = 992.5 px at eave depth. That converts to 948 px at bird depth, giving **15.4 m**. If only the roof planks counted (about 926 px), the answer would be 6% lower.
- Bird body length (beak to tail tip, plateau frames): about 128-134 px; I used 130 px, giving **2.11 m**.
- Wingspan (largest tip-to-tip distance across flap cycles, frames 0, 1, 17 and 50): 255-259 px; I used 258 px, giving **4.19 m**.

## Confidence
All three answers scale as 1/v, so the main risk is which speed the "6 m/s" prior refers to.
- If it means the peak or mid-clip speed, all three answers are about 25% too high.
- If it means the keyframe average, they are about 10% too low.

Other errors are smaller: about 3% on pixel extents and about 4% on the eave-depth factor.
- Q5 (house): medium-low.
- Q6 (body length): medium-low.
- Q7 (wingspan): medium-low.
