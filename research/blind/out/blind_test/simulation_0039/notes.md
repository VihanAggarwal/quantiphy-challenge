# simulation_0039: notes

## Video and frames
- 1536x1536, 75 container frames at 25 fps. These are 72 dataset frames at 24 fps plus 3 duplicates (video frames (0,1), (25,26) and (50,51)).
- Video frame k maps to original frame floor(24k/25). Every script works on the de-duplicated original frames (scripts/common.py), so t=1 s is original frame 24.

## Camera
- Focal length: the boat moves at 4 m/s (the prior) and translates without rotating. Template tracking gives a pixel displacement of (-193.4, -54.1) px between t=1 and t=2. Using P = r * ray(u,v) with the given ranges 177.21 and 178.00 m, |P2-P1| = 4 m gives f = 9072 px (HFOV 9.7 deg). The optical-axis-Z convention would give f = 9127 px.
- Pitch: the vertical vanishing point from the mast lean across 64 frames is at (698, 7234), which gives a 54.5 deg depression and 0.6 deg roll (bootstrap 53.7 to 55.3).
- Cross-checks: under the range convention the boat moves horizontally at 54.1 deg (Z convention: 51.6 deg). The eagle moves horizontally at 52.7 deg. The person's image height (~62 px) fits a ~2 m human. Range convention adopted.
- The human depth data is inconsistent with walking on flat ground. The image motion is 50.7 px/s downward, yet the range increases by 0.09 m/s. This means the pelvis descends about 0.69 m/s. The eagle shadow moves non-uniformly over the sand, which suggests sloped terrain, so the depth data was trusted.

## Answers
- 1154, person speed at t=1: the 3D chord from image track plus ranges is |dH| = 1.036 m/s, answered as 1.04. Medium confidence. If the person really walks on flat ground the answer would be about 1.28.
- 1155, boat length: bow tip to stern on the deck plane, rectified, is 9.75 to 10.0 m. Answered 9.85. Medium-high confidence.
- 1156, boat width: the near gunwale (white to red edge) and far gunwale (bulwark cap) rectified on the horizontal plane give 3.05 m at the widest visible station, and the width rises toward the hidden mid-ship section. Answered 3.05. Medium confidence.
- 1157, eagle length: extent along the heading on the rectified horizontal plane is 0.80 to 0.84 m over the flap cycle. Answered 0.83. Medium confidence.
- 1158, eagle wingspan: extent across the heading at the flap peaks is 1.87, 1.93 and 2.11 m. Answered 2.0. Medium confidence.
- 1159, eagle speed at t=1: the smoothed chord with ranges is 11.54 m/s. At t=1 the transverse component is 11.27 m/s and the radial component is -2.53 m/s for straight-line motion. Answered 11.5. High confidence.
