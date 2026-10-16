# Lab audit: family 0031 (captured_0031 / 0031s / 0031x)

This family has one event. A tennis ball (6.7 cm, stated) and a white ball rest near the back edge of the lab
table during frames 0-15. Both then roll toward the camera. The tennis ball goes off the front edge at about
frame 43; the white ball is still rolling at frame 48.

The camera is low, about 17 cm above the table top, so the table is seen at a grazing angle. All three renders
have 49 frames, 24 fps and 1280x720. The tracks agree to 1 px between the base and x renders. The s render shows
the same event: the white ball is a grey disc at the same pixel position, but it is barely separable from the
whitish background before frame 38.

Scripts are in `scripts/`:
- `extract.py`: frames and montages.
- `track.py`: HSV tracks.
- `circfit.py`: edge circle fits.
- `geom.py`: table edges and corners from the x-render mask at frame 48.
- `plane.py`: table plane from vanishing points.
- `routes.py`, `speed.py`, `profile.py`: plane route and ball-size route.
- `dist.py`: ball-to-ball distance.

Frames and crops are in `frames/`.

## Geometry
- **Table corners (x render, frame 48):** BL(574.3,424.3), BR(849.7,428.1), FR(963.2,495.0), FL(462.4,482.7).
  The front edge is 501 px long and the back edge 275 px.
- **Plane at f=711:**
  - Rectified aspect L/W = 1.175. The known table is 1.26, and f=760 would give 1.253; the grazing view
    leaves the depth aspect poorly conditioned.
  - Camera height above the table is 16.8 cm (W=60.3 scale) or 18.0 cm (L=76 scale).
- **Ball-size route** (f=711, tennis 6.7 cm, white 4.0 cm) against the plane route for the ball-centre range:
  - Tennis: Rplane(W) / Rsize = 1.00-1.06.
  - White: 0.98-1.00 with the circle-fit diameter (the mask diameter is about 5% low because the shaded
    underside is missed).
  - So the plane's W scale is consistent with the ball sizes.

## Stated depths are physically inconsistent (but the label uses them)
- Stated at t=1.6 s: tennis 1.190 m and white 0.994 m.
- Measured at frame 38.4: tennis centre range about 0.92-0.96 m and white about 1.14 m (plane and size
  routes).
- No single frame satisfies both stated values. The names look swapped, or the ToF hit something else.
- For the distance this does not matter. The two rays are only about 78 px apart, so
  |1.19 e_t - 0.994 e_w| = |0.994 e_t - 1.19 e_w| = 22.8 cm.

## Rows

| qid | render | question | current | measured (routes) | verdict |
|---|---|---|---|---|---|
| 2520/2526/2532 | 0/s/x | white ball diameter | 4.0 | See the diameter note below | OK |
| 2521/2527/2533 | 0/s/x | table width | 59.6 | Front/back edge is the short side. Ball-size-scaled plane gives 57-63 cm; known lab table 60.3 | OK |
| 2522/2528 | 0/s | table length | 74.5 | Edge-length route gives 70 at f=711 and 75 at f=760 (ill-conditioned); known table 76.0 | OK (within 6%) |
| 2523 | 0 | v tennis at 1.6 s | 77.52 | Plane 51-64, size(mask) 51-62 cm/s | Keep (inside tuned-correction regime, below 1.5x) |
| 2529/2534 | s/x | v tennis at 1.6 s | 71.84 | Same as above | Keep |
| 2524 | 0 | v white at 1.6 s | 47.76 | Plane 42.3-46.7, size 42-52 (fits over frames 30-46; 24 or 25 fps index) | OK |
| 2535 | x | v white at 1.6 s | 45.6 | Same as above | OK |
| **2530** | **s** | **v white at 1.6 s** | **30.0** | **Same label: about 46** | **FIX to 46.7** |
| 2525/2531/2536 | 0/s/x | white(ping-pong)-tennis distance at 1.6 s | 22.78/23.58/22.92 | Stated-depth back-projection 22.4-23.4 (f 650-760; 22.8 at f=711), plane 22.0-23.7, size 23.6-26.6 | OK |

### White ball diameter (rows 2520, 2526, 2532)
- The question text and depth_info of 2525 and 2536 name it the ping-pong ball, and the ping-pong ball is stated
  as 4.0 cm or 40 mm in other lab clips.
- Measured:
  - Plane route at rest (frames 0-14, circle-fit d = 17.3 px): 3.92 cm (W scale) or 4.25 cm (L scale).
  - Plane route at frame 38 (d = 24.8 px, R = 114.6): 4.00 cm.
  - Same-depth ratio to the tennis ball at rest (both at plane range 161 cm): 6.7 x 17.3 / 30.7 = 3.8 cm.
- Taking the stated 0.994 m literally gives 3.5 cm, but that depth is inconsistent (see above). Swapping the
  two stated depths gives 4.2 cm.

## The one fix: qid 2530 (captured_0031s, white ball speed at 1.6 s), 30.0 -> 46.7
- **Why 30.0 is wrong:** `research/labnoise/out/test_rows_cap1.6.csv` has the same base measurement p8 = 30.0 on
  all three renders.
  - The label-noise emulator gave factor 1.592 on the base render (giving 47.76) and 1.52 on x (giving 45.6).
  - On s the emulator had no track: sin_psi is NaN and the factor is 1.0, because the white ball is invisible
    on the s render's white background. My own HSV tracker also fails there before frame 38.
  - So 30.0 is the uncorrected value, a pipeline artefact. It is not a measurement of the s video, and the s
    video shares the same label as the base and x renders.
- **Measurement of the white ball speed at t=1.6 s** (smoothed fits over frames 30-46, evaluated at frame 38.4
  at 24 fps or frame 40 for a 25 fps index):
  - Route A (ray-plane intersection with the ball centre at r above the table): 42.3-43.1 (W scale) and
    45.4-46.7 (L scale), mean about 44.4.
  - Route B (range from apparent size with D = 4.0 cm): mask diameters 42.1-51.1 and circle-fit diameters
    41.8-52.4, mean about 47.4.
  - The two routes agree within 7%.
  - The 4-frame plane profile is steady at 40-53 cm/s around frames 30-42, decelerating from about 55 cm/s.
  - Scaling f to 760 raises every route by about 7%.
- **Proposed value:** 46.7, the mean of the sibling renders' tuned answers 47.76 and 45.6. It lies within my
  measured 42-52 range. The current 30.0 is 1.5-1.6x below both the measurement and the shared-label siblings.
  The base and x rows need no change.

## Verdict
There is one fix, qid 2530: 30.0 -> 46.7, to match the same-label renders 2524 and 2535. The other 16 rows are
consistent with my measurements or sit inside the leaderboard-tuned motion regime.
