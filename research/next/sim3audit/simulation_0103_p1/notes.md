# Audit simulation_0103_p1 (beach family: boat 10 m, eagle 0.8 m, person 1.75 m)

55 scored rows in 15 clips. 33 rows are stated facts and were left alone. I checked the 22 measured rows against the family and re-measured the suspect ones on frames.

## Family table (measured rows)
| quantity | values (clip: answer) | verdict |
|---|---|---|
| boat height | 0022 9.6, 0023 9.75, 0024 9.5, 0026 9.4, 0029 9.8, 0031 8.96, 0036 9.5 | consistent (median 9.5; 0031 is -6%) |
| boat width | 0024 3.3, 0031 3.16, 0039 3.05, 0043 3.12 | consistent |
| eagle wingspan | 0023 **2.5**, 0025 2.05, 0028 1.96, 0031 1.86, 0035 2.1, 0039 2.0, 0040 1.95, 0044 1.88 | 0023 is the outlier (flagged below, but not fixed) |
| eagle speed | 0025 11.8 | 0025 is the same footage as 0023, where the prior is 11.84 m/s. This is fine. |
| person speed | 0027 **1.0** | Every sibling with a stated value has 1.3 (0026, 0035, 0036, 0039, 0040; also the priors of 0025 and 0031). **Fix.** |
| rock width | 0043 25.5, 0044 24.8 | Same camera and same rock. Consistent. |

Camera identities (from identical median backgrounds and depth_info):
- 0027 is the same camera as 0028. Phase correlation of the medians gives a shift below 0.01 px, with a mean absolute difference of 0.6 grey levels.
- 0023, 0025 and 0026 share one camera. 0023 and 0025 show the identical eagle track (116.0475 -> 108.2756 m).
- 0043 and 0044 share one camera.

## qid 1116, 0027 person speed 1.0 -> 1.3 (FIX)
Why 1.0 is wrong: the agent took the camera depression to be 26 deg. This came mainly from assuming a "natural" step length of 0.66-0.78 m, plus the aspect ratio of the rock outline. At 26 deg, the toward-camera component of the walk (which is mostly down the image) is underestimated.

Re-measurement (scripts track27.py, meas27.py, fit28.py, geom.py, speed27.py):
- **Focal length.** 0028 has the same camera. Its stated eagle speed is 11.90374 m/s, with ranges 100.1405 / 99.5206 m. The smoothed eagle track (body centroid with flap harmonics removed) is (456.9, 243.9) at 1 s and (864.8, 254.6) at 2 s. Together these give f = 3404 px. This agrees with the 0028 agent's body-length value of 3411.
- **Pitch.** The eagle is assumed to fly level, as in the other family clips. Its 3D chord from t=1 to t=2 is (11.83, +0.40..0.48, -1.22) m. Phase-matched vertical drift is 12.7 px/s at t=1-2, or 10.7 px/s as a whole-track average. This gives a pitch of about 20.4 deg (18.0 from the whole-track average). The ray to the person is about 1.5 deg less steep than the optical axis.
- **Person track.** I used a median background and the white-shirt centroid. The constant-velocity fit over all 75 frames gives (11.28, 14.94) px/s. Pixel height (sole to head top) is 58.5-60 px.
- **Ground speed.** I back-projected the track onto the horizontal plane, with the scale anchored to the 1.75 m height prior. The results are 1.36 m/s at pitch 20, 1.33 at 20.4, 1.29 at 21 and 1.44 at 19. The 1-s chord, which is not gait-phase matched, gives 1.25-1.27. Anchoring to the depth label instead (100.56 m) gives about 7% more.
- **Agent's own table.** The 0027 agent's formula, extrapolated to a depression of 19 deg, also gives about 1.3.

Family check: the gait period in 0027 is 17.75-18.5 frames per step and 34.5-36 frames per stride. This matches 0025's 35.5-frame stride. So it is the same walk cycle, and its stated speed is 1.3 m/s in 5 clips.

Result: the in-clip estimate (1.33-1.37) agrees with the family value (1.3) within 5%. The current answer is 23% low. **Proposed value: 1.3.**

Caveats:
- The level-flight pitch assumes zero camera roll. A roll of 0.5 deg moves the pitch by about 4 deg.
- A joint shadow fit (eagle shadow in 0028 plus the person's head-shadow tip in 0027; shadowfit.py) was inconclusive, with 4-8 px residuals. Its person-shadow term alone prefers a pitch of about 20 deg.

## qid 1105, 0023 eagle wingspan 2.5 (flagged, NOT fixed)
- 0023 and 0025 are the same footage, but their answers differ: 2.5 vs 2.05.
- The other cameras give 1.86-2.1. Scale-free W/L ratios of about 2.35-2.5 from 0028, 0039, 0040 and 0044 point to about 1.95-2.0.
- My in-clip measurement (eagle23.py, crop23.py) uses edge-on, wings-flat frames: frame 33 at 48 px and 113 m, frames 55-56 at 43.5 px and 106 m, and frame 8 at 44 px and 121 m. These give projected spans of 1.36-1.60 m at f = 3390.
- If the body is aligned with the velocity (41 deg from the image plane, with an image-position-dependent foreshortening factor of 0.58-0.70), W comes out at 2.26-2.51. If the body is yawed about 10 deg further toward the line of sight, W comes out at about 2.0. The white head sits 6-7 px ahead of the wing centre, which cannot separate these two cases.
- So the in-clip route does not agree with 1.95 within 8%, and I do not propose a fix.
- Note for the orchestrator: two rows answer different values for one physical quantity. A common hedge of about 2.2 for both 1105 and 1111 would cap the error at about 12-15% whichever end is true.

## Other notes
- Rock (not in this item): the p2 pre-agent rows for 0024s, 0027s and 0028s give rock width 8.5-10 and length 18.55. These do not fit the 0043/0044 view of the same rock, where it spans about 500 px against the 10 m boat's 228 px at a similar range, so its largest horizontal extent is about 22-25 m. Worth checking in the p2 audit.
- 0022-0031 have 75 genuine frames (25 fps container, no duplicate frames); the dataset fps is 24. I used frame/24 throughout.
