# internet_0013 — drone top-down view of a turbo roundabout (1920x1080, 30 fps, 9.3 s)

## Camera / scale
- The camera is a near-static nadir drone shot. Phase correlation on static patches shows a total drift of 1-3 px over 9 s, which is negligible. The planter fits a circle (ellipse axes 447.2 / 448.3 px), which confirms the nadir view, so one m/px scale is used for the whole frame.
- Prior: a pedestrian walks at ~1.1 m/s. The pedestrians on the left sidewalk were tracked by background subtraction against the median frame, then checked by eye on zoomed montages:
  - group of 3 (a pair plus a third person): ~23-26 px/s, about 24.5 px/s on average
  - single walker C: 23.5 px/s on average (slows from about 27 to 21 px/s)
  - 1.1 / 24.5 = 0.0449 m/px
- Cross-check: the zebra-crossing stripe period at the NW arm is 22.8 px. With 0.5 m stripes and 0.5 m gaps (Polish P-10 marking), that gives 0.0438 m/px.
- Car lengths are 107-116 px, which is 4.8-5.2 m at 0.0445. That is plausible.
- **Adopted scale: 0.0445 m/px.**

## Measurements (px -> m)
- Planter (vegetated centre disc): fitted circle centre (961.7, 533.0), D = 447.7 px -> **19.9 m**. The paved apron ring extends the island to D = 546 px (24.3 m); the apron is not counted as planter.
- Circulating ("roundabout") lane: apron edge at r = 273 px, lane-divider line at r ≈ 364.5 px, outer curb at r ≈ 458 px. The inner lane is 91.5 px and the outer lane 93.5 px, so about 92 px -> **4.09 m**.
- "Straight-through lane": taken as a lane of the straight main road (SW and NE arms), measured on rotated crops:
  - SW exit lanes: 81 and 82 px
  - NE exit lanes: 81 and 68 px
  - about 80 px -> **3.56 m**
  - Alternative reading: the outer circulating lane, 93 px = 4.1 m.
- White car at 3.0 s: the white SUV circulating at the top right (centroid of its bright body mask). Backward and centred differences over frames 80-95 give 4.28-4.35 px/frame, about 130 px/s. The other white car (a wagon in the south part of the ring) gives 133 px/s. Using 131 px/s -> **5.83 m/s**.
- Bicycle (upper-left, crossing the NW zebra crossing) at 3.0 s:
  - centroid of the foreground difference along its path: linear fits over windows from 80-100 to 50-130 frames give 69-71 px/s
  - head positions read by eye: 69.8 px/s
  - result: 70 px/s -> **3.11 m/s**
- Two black cars in the roundabout at 1.0 s: body centres from the four corners are (617, 341) and (1178, 182). The centre-to-centre distance is 584 px -> **26.0 m**.

## Confidence
- 2202 planter diameter: medium-high (main uncertainty is the scale, ±5%).
- 2203 white car speed: medium-high (both white candidates agree within 3%).
- 2204 bike speed: medium-high.
- 2205 distance: medium (assumes centre-to-centre).
- 2201 roundabout lane: medium (could be read as the whole 2-lane ring, 185 px = 8.2 m).
- 2200 straight-through lane: low-medium (ambiguous which lane is meant; arm lanes are 68-82 px, the outer ring lane is 93 px).
