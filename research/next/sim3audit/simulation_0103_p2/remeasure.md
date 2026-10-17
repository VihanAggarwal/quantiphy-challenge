# simulation_0103_p2: independent re-measurement

Scope: qids 1682, 1692, 1698, 1670, 1680, 1690, 1696, 1671, 1681, 1691, 1697, 1693, 1668 and 1676.
Scripts and crops are in `remeasure_work/` (scripts/, frames/). I did not read any other file in this directory.

## Camera structure (from the frames)
- 0024, 0027 and 0028 share one camera, called C1. It has three objects with known values: the boat (4 m/s, 10 m), the person and the eagle (0.8 m, 11.90 m/s).
- 0043 and 0044 share camera C2, which looks steeply down.
- 0039, 0040 and 0042 use camera C3. C3 has the same orientation as C2 but a longer lens (f about 8550 px at 1536 px).
- 0023, 0025 and 0026 share camera C4, a near-horizontal view from a different azimuth.
- 0022 is a low near-horizontal view.
- The rock is the same object in every clip, so one value applies per dimension.

## Registration method
- For each camera:
  - f comes from the 4 m boat chord between t=1 and t=2, using the Euclidean ranges, and is cross-checked with the eagle chord, the eagle length and the boat deck length.
  - Pitch d assumes roll 0, horizontal boat motion and level eagle flight.
  - Each camera is placed in a common "boat frame": origin at the boat at t=1, X along the boat heading, Z up.
- Validation: the eagle's 3D path, reconstructed independently in C1, C2 and C4, agrees within about 0.6 m (Y about -12.3, Z about +6.2).
  - The eagle flies exactly along -X, so the boat and the eagle share one world axis. Both have their stated "length" along X.
  - Naming is therefore length = X, width = Y, height = Z. A max/min naming is ruled out: the eagle's length (0.8) is less than its wingspan.
- Values used:
  - C1: f 3460, d 19.4.
  - C2: f 3860, d 54.5.
  - C3: f 8550, d 54.6. Check: eagle plan-view X-extent median 0.80-0.82 m against the stated 0.8.
  - C4: f 3420-3500, d about 0.4.
  - 0022: f 4350-4500.
  - Sand plane at the rock: z = -0.6, fitted jointly from the near-base contours in C1 and C4 and the 0022 base.

## Rock (one value for all clips)
- Footprint: the C2 silhouette is back-projected onto the sand plane.
  - X range is -9.8 to 14.1, so X = 24.0 m. Calibration range is 23.5-24.4.
  - Cross-checks:
    - Projected into C1 it covers x 326-955. The observed rock spans 326 to at least 959 (clipped at the frame edge), so X ≥ 24.
    - The left end in C4 matches to within 5 px.
- Y extent:
  - The near base is at -28.4 and is reliable: it agrees between C1, C2 and C4.
  - The C2 far silhouette hits the ground at -60.8. It is inflated by s·cot(47°), where s is the height of the far tangent point.
  - The C1 top-silhouette rays limit s to 1.8 m or less, so the far base lies between -60.8 and -59.0.
  - Y = 31.5 m, range 30.5-32.5, with an extra ±3% from f and d.
- Height:
  - 0022 near-horizontal profile: the peak column is 106-108 px above the base.
    - The pure f/range route gives 4.5-4.7 m.
    - Note: 0022 looks about 5-9% narrower than the C1/C2/C4-consistent footprint predicts, so its scale is suspect.
    - The ratio route (height px / width px × the 24.3 m perpendicular footprint width) gives 4.9-5.0 m.
  - C4 silhouette at the frame edge, over the X+ shoulder: 4.1-4.4 m or more.
  - C1 top-silhouette rays are consistent with a broad top of 4.6-5.0 m.
  - Adopted height 4.9 m. This assumes no deep buried part.
- Answers:
  - Length (1670, 1680, 1690, 1696) = **24.0 m**.
  - Width (1682, 1692, 1698) = **31.5 m**.
  - Height (1671, 1681, 1691, 1697) = **4.9 m**.
- Risks:
  - If the dataset names the axes the other way, length and width swap (24 against 31.5).
  - The far-side profile of the rock.

## Person speed (1693 on 0027, 1668 on 0022)
- Every stated person speed in this family is 1.3: clips 0026, 0035, 0036, 0039 and 0040, plus the priors of 0025 and 0031.
- The person's depth labels do not follow the visible walker. In 0027 the labelled range is about constant, but the walker visibly approaches. The same happens in 0025/0026, where 1.3 is a stated fact.
- C1 route: I projected the 0027 feet onto the fitted sand plane. The speed is 1.32 m/s over t=1→2 and about 1.5 averaged over 3 s (gait noise).
- In 0022 the person is not visible: the segmented clip contains only the rock and the boat. 1668 relies on the shared scripted walker.
- 1693 = **1.3**, 1668 = **1.3**.

## Eagle wingspan (1676, 0023; same eagle model in every clip)
- C3 0039, plan view: the silhouette is back-projected to the eagle's height plane.
  - Maximum Y-extent per flap cycle: 1.91 (f6), 1.95 (f33) and 2.18-2.21 (f56-58, wings straightest). The f56-58 value is stable across thresholds 40-70.
  - Body X-extent is 0.75-0.85, against the stated 0.8.
- C2 0044 at low resolution: 1.78, corrected for edge loss to about 1.9.
- Fully spread span is taken as at least the largest plan-view value: **2.2 m**, range 2.1-2.35.
