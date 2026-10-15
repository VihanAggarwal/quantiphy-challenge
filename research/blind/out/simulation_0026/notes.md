# simulation_0026 notes

Scene: static camera (checked by phase correlation on the cliffs and sand, drift under 0.05 px), 960x960 px, 75 frames, 24 fps.
A red fishing boat moves left and away from the camera. A person on the beach drifts left and slightly down in the image,
at constant range: depth_info gives 114.832 m and 114.836 m for the person, and the person's pixel height stays at about 54 px.

## Focal length from the prior
- Person height, measured to sub-pixel from head top to shoe bottom using a background with the person excluded:
  54.2 px at t=1 (frames 15-37 average about 54.1, whole-clip average about 53.8).
- f = 54.2 * 114.83 / 1.75 = about 3555 px. The range of plausible values, 3530-3580, changes the answers by about 1%.
- That gives a horizontal FOV of about 15 deg. The horizon is at v of about 440 (fitted from the vertical image motion of
  the mast top and the hull stripe as the boat recedes), so the camera pitch is about 0.6 deg down.

## Boat motion and heading
- I tracked the bow tip, the stern/rudder and the mast top over frames 0-63 with scale-compensated masked template matching.
- Fitting the bow track (rms 0.25 px) together with the two boat ranges (103.157 m, 106.091 m) gives:
  - motion direction 44.0 deg from the image plane, going away and left;
  - speed 3.96 m/s.
- A fit with the heading left free gives 39.5-44 deg, consistent with the boat moving bow-first.

## Q1114: boat length
- At t=1 the bow tip is at u=195 and the stern centreline (rudder, middle of the transom) is at u=424.
- With the heading taken as the motion direction and perspective included, L = 9.68 m.
- If the heading is set by the free fit instead (39.5 deg), L = 8.96 m.
- Answer: 9.6 m. Confidence medium; the main uncertainty is the heading.

## Q1113: boat height
- At t=1 the mast top is at v=305.5 and the lowest hull/water boundary is at v of about 627 (at x of about 340).
- Correcting for each point's depth (horizon v of about 442) gives a height of 9.29 m.
- This assumes the hull is not submerged; the rudder and propeller are visible above the water.
- Answer: 9.3 m. Confidence medium-high, unless there is a hidden submerged draft.

## Q1115: person speed at t=1
- The pelvis moves in the image plane, since the range is constant.
- Upper-body template and torso centroid tracking:
  - x rate 0.53-0.54 px/frame;
  - y rate 0.14 px/frame on average, but about 0.22-0.30 px/frame around frame 24 (vertical gait bob on top of a steady
    descent).
- Local image speed is about 14.0-14.7 px/s, giving 0.45-0.48 m/s. The whole-clip average is 13.2 px/s, giving 0.43 m/s.
- Answer: 0.46 m/s. Confidence medium; the gait phase makes the instantaneous value uncertain by about 10%.
