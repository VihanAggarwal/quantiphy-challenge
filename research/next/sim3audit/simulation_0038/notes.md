# sim3audit: simulation_0038 (clips 0037, 0037_segmented, 0038_segmented)

Result: **no fixes proposed.** All 7 rows checked. Two rows (the rock lengths) are inconsistent with each other, but there is no single value that two independent routes agree on, so neither row meets the fix bar.

## Family

This is the beach scene of 0022-0044: the red boat AH805, the eagle, the person in the white shirt, and one large boulder on the sandbar.

- 0037 is a low camera looking across the water. 0038 is a high camera looking down at about 49 deg.
- The person is the same model in every clip of the scene. 0035 states "height of the person = 1.75 m", and 0035 has the same human depths as 0036. The person also walks at 1.3 m/s here, the same as 0036 and 0039 (stated).
- The rock is the same object everywhere: the same skirt of vertical stripes, and the same dark streaks on the east side. 0022, 0030 and 0037 show it from the side. 0024, 0027 and 0028 show it from above at an angle. 0038, 0039, 0040, 0043 and 0044 show it from the top.

| qid | clip | quantity | current | provenance | family / my check |
|---|---|---|---|---|---|
| 1153 | 0037 | person height | 1.75 | pre-agent | family 1.75 (0035 prior). Keep. |
| 1730 | 0037_seg | person height | 1.75 | pre-agent | same. Keep. |
| 1735 | 0038_seg | person height | 1.75 | pre-agent | same. Keep. |
| 1731 | 0037_seg | rock length | 21.9 | pre-agent | family: 18.55 (0022/24/27/28, pooled pre-agent), 28.2 (0038). Re-measured: AABB is ambiguous, 19.5-30.5 m. No fix. |
| 1732 | 0037_seg | rock height | 3.7 | pre-agent | family pooled 7.8 (0022-0028). Re-measured visible height 3.8-4.1 m. Keep. |
| 1733 | 0038_seg | rock length | 28.2 | pre-agent | matches the forward ground extent at z=0 (28.5). No fix. |
| 1734 | 0038_seg | rock width | 25.2 | pre-agent | 0043 25.5 and 0044 24.8 (agents). Lateral extent 23.1. No fix. |

## Person and depth (0037 and 0038)

- **0037_segmented** (scripts/person37.py, crop37.py)
  - The image speed is 41.37 px/s horizontally and 2.5 px/s vertically.
  - Height from head top to sole is about 58-61 px. The earlier agent measured 61-62 px.
  - The scale from height is 1.75 / 60 = 34.3 px/m. The scale from speed, if the walk were perpendicular to the line of sight, is 41.4 / 1.3 = 31.8 px/m.
  - These two agree only if the walk is about 22 deg oblique to the image plane (cos = 0.93).
  - The given human depth hardly changes (122.857 -> 122.859). That does not follow the visible walk: in 0038 the person walks toward the camera at 33 px/s, yet the depth rises by 0.09 m/s. The same is true in 0039.
  - So the speed-based scale is inflated by about 8%. That is exactly why the blind agent for 0037 got 1.95 m: 1.95 x 0.93 = 1.81, and 1.75 m with my 60 px. **1.75 stands.**
- **0038_segmented** (scripts/geo38.py)
  - The video is 25 fps with duplicate frames at (0,1), (25,26) and (50,51). Original frame = floor(24k/25).
  - The head moves (1.96, 33.17) px/s, nearly straight down. The person therefore walks along the camera's forward ground axis, toward the camera.
  - The projected height is a median of 38.5 px (IQR 36-41).
  - From 1.75 m and 1.3 m/s together: depression delta = 49.3 deg and f/R = 33.7 px/m.
  - With R = 179.1: f = 6036 px, f/W = 3.93, HFOV 14.4 deg.
  - 0037 gives f/W = 4214/1080 = 3.90, the same lens. That suggests the depth magnitudes are right even though their rates are not.

## Rock: plan from 0038 and cross-check with 0037 (scripts/rock38.py, plan38.py, cross3738.py)

- The 0038 rock outline was projected onto the ground with the camera above: near edge at z=0, far (top) edge at z = 0, 2 or 4 m.
- Extent E(theta) along a horizontal direction theta, measured from the image-x axis toward forward, at k = 33.7:
  - 0 deg: 23.1 m
  - 30 deg: 28.1 m
  - 55-60 deg: 30-31.5 m (maximum)
  - 90 deg: 25.5-28.5 m
  - 120 deg: 21-25 m
  - 150 deg: 19.5-20.7 m (minimum)
- k = 32.5-35 shifts these by about ±4%.
- The rock is elongated from SW to NE in the 0038 frame. Any world-axis AABB therefore has dimensions between about (19.5, 30) and (23, 27).
- **Cross-check against 0037.** Place the 0037 camera on the 0038 map at its person-depth distance, with the 0037 height scale of 34.3 px/m, and scan its viewing azimuth.
  - Best fit: the azimuth is 22 deg off the 0038 lateral axis.
  - The predicted silhouette ends are x = 8 and x = 714. The measured ends are x = 15 and x = 715.
  - The 22 deg azimuth matches the walk obliqueness found from height and speed, an independent cue. The 0037 scale, the 0038 scale and the map therefore agree.
  - The rock lies 13-20 m beyond the person in 0037. The pre-agent pipeline instead put it at the person's depth and used the inflated speed scale: 700 px x 0.0314 = 21.9 and 115 px x 0.0314 = 3.6.
- **Rock height (1732).** The tallest silhouette column in 0037 is 115 px (x = 136: top 595, base 710). At the summit depth (+17 to +28 m beyond the person) the scale is 27.9-30.1 px/m, so the height is **3.8-4.1 m** (about 0.3 m less if the camera's small elevation is allowed for).
  - The current 3.7 is within 10%. Keep.
  - The family's pooled 7.8 (0022-0028) is not supported by 0037. The 0043 agent's "8.3 m cliff" came from a top view.
  - Parts of the mesh below the sand, or lower ground on the east side, cannot be seen in any clip here.
- **Rock length (1731, 1733) and width (1734).** The answer depends on which way the world axes run, and nothing in the scene settles that.
  - The person walks exactly along the 0038 forward axis. If that axis is world Y, the AABB is about (23.1, 26.5 ± 1.5): one of 21.9 and 28.2 is then 15-22% off and the other is within 5%.
  - The 0039 boat path is about 19 deg off the 0038 lateral axis. If the boat runs along a world axis, the AABB is about (21, 30).
  - The two hypotheses give different answers, so there is no two-route agreement. No fix.
  - The family requires 1731 and 1733 to be equal. A possible hedge, not proposed, would be about 25 for both: it is within about 8% under either hypothesis.

## For the 0022-0028 audit (not my rows)

- The pooled rock widths of 8.5-10.0 (0024, 0027, 0028) cannot fit this rock: its plan extent is at least about 19.5 m in every direction.
- The pooled height of 7.8 is about 2x the visible height in 0037.
- The pooled length of 18.55 is what you get by putting the rock at the boat's depth in 0022 (525 px at about 28 px/m).
