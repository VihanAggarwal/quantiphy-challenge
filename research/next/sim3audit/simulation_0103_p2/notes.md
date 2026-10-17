# Audit simulation_0103_p2 (beach family: boat / eagle / person / rock)

Scripts are in `scripts/`. Key frames and overlays are in `frames/`. Labels were not used.

## 1. Family table (the same object across clips)

| quantity | values (clip: answer [provenance]) | verdict |
|---|---|---|
| boat height | 22s 9.6, 23s 9.75, 24s 9.5, 26s 9.4, 29s 9.8, 31s 8.96, 36s 9.5, 39s 10.03, 43s 10.03 | consistent (median 9.6); keep |
| boat width | 42 3.16, 24s 3.3, 31s 3.16, 39s 3.05, 43s 3.12 | consistent; keep |
| eagle wingspan | 42 2.05, 25s 2.05, 28s 1.96, 31s 1.86, 35s 2.1, 39s 2.0 (p1: 40 1.95, 44 1.88), **23s 2.5** | 23s is an outlier. 23s and 25s are the SAME eagle take in the same camera (identical eagle depths) but got 2.5 vs 2.05 |
| eagle speed | 25s 11.84, 39s 11.84 [pre-agent] | 25s shares its take with 0023 (prior 11.84); 39s shares its take with 0042 (prior 11.84); keep |
| person speed | stated 1.3 in 26s, 35s, 36s, 39s (and 40); prior 1.3 in 25, 31; **22s 4.15** [pre-agent], **27s 0.57** [pre-agent] | 22s and 27s are wrong |
| rock length | 22s, 24s, 27s, 28s: 18.548 [pre-agent, one propagated value] | too small (see 3) |
| rock height | 22s, 27s, 28s 7.8; 24s 7.78 [pre-agent] | too large (see 3) |
| rock width | **24s 10.000000000000002, 27s 8.5, 28s 8.8** [pre-agent] vs 43s 25.5 [agent] (p1: 43 25.5, 44 24.8) | bimodal; the 8.5-10 values are wrong |

Cameras (same viewpoint, same rock position in the image): A = 0024/0027/0028 (960 px, about 19 deg down), C = 0043/0044 (1080 px, about 53 deg down),
B = 0023/0025/0026 (low view; the rock is cut off at the right edge and is not segmented), 0022 (near-horizontal view; the rock is fully visible),
D = 0039/0040/0042 (rock cut off).

## 2. Calibration and cross-camera registration (scripts/reg.py, reg_check.py)

- Per camera, f comes from the depth chord: |P(t2)-P(t1)| = prior speed, with P = range * ray, Euclidean range convention.
  - A: boat gives 3517, eagle gives 3401.
  - C: boat gives 3949, eagle gives 3799.
  - B: boat gives 3493, eagle gives 3390.
  - 0022: boat gives 4350-4625. The boat height of about 9.5 m gives about 4570.
  - Eagle-based f is about 3.5% below boat-based f in every camera. The spread used is +-2%.
- Pitch (roll 0) comes from the boat's horizontal motion: A 18.7 deg (as in the 0024 agent's multi-route value), C 53 +- 2 deg, 0022 about -1.3 to -1.8 deg.
- World frame W: origin at the boat hull centroid at t=1, X along the boat's motion, Z up. Each camera is registered through its own boat track.
- Check: the eagle's t=1 and t=2 positions, computed independently in A (0028) and C (0044), agree within about 1 m (eagle at Y about -12, z about 6, flying along -X).
  The rays through the rock-mask centroids from A and C meet within 0.03-0.2 m. The registration is good to about 1 m.

## 3. Rock (scripts/vhull*.py, footprint*.py)

- Visual hull from the segmented rock masks of A (0027s), C (0043s) and 0022s, with all three registered in W.
  Coverage of each view's mask is 0.92-0.98 for good parameters. The 0022 view constrains height; A and C constrain the footprint.
- The A and C near-base points coincide (Y about -29.3) only if the rock base is at z about -1 in W (about 0.5 m above water). The hull bottom is also there.
- Results across f, pitch and 0022-parameter variants:
  - **X extent (along the boat motion axis) 22.4-24.1 m**:
    - A ground footprint 22.4-24.1
    - C ground footprint 22.4-23.4
    - 3-view hull 22.8-24.0
  - **Y extent (perpendicular horizontal) between 23.5 and 32.5 m**:
    - lower bound: C's top-silhouette ray at the apex height is at Y about -52
    - upper bound: hull at base level
    - likely about 26-31
  - **Visible height (base to apex) 5.0-5.25 m** from the 3-view hull. The apex is in 0022.
    - From the 0022 frame geometry (horizon 600-618 px, boat waterline 680 px, rock at 188-206 m), the apex is 5.5-6.1 m above the water level.
    - The 0022 apex-to-boat-mast ratio gives 5.1-5.7.
- Why the pre-agent values are wrong:
  - *length 18.548*: this equals the 0022 rock bbox width (527 px) times the boat scale at the boat's depth (10 m / about 284 px = 18.5).
    The rock is 188 m from the 0022 camera, not 148.7 m. The depth-corrected value is 18.55 * 188/148.7 = 23.45, which matches X from A and C.
  - *widths 8.5 / 8.8*: these are camera A's image-vertical rock extent (285 px) times 2D reference scales: person 1.75 m / 58.7 px gives 8.5; eagle 0.8 m / about 26 px gives 8.8.
    In a 19-deg-down oblique view that extent is mostly foreshortened depth plus height, not width.
    *24s 10.000000000000002* is a degenerate ratio: it is exactly the boat length, so the same box was used for the rock and the boat.
    Every horizontal extent of the rock is at least 22 m. Camera C's top view shows a rounded, egg-shaped footprint, not a 9 m-wide slab.
  - *height 7.8*: no depth-consistent route gives this. It matches camera A's central vertical extent (264 px) times the person scale (0.0298 m/px), which again mixes depth into height.
- Caveat for height: the AABB of the mesh could include rock buried below sand or water.
  For 7.8 to be right, at least 2 m of hidden mesh would be needed. I propose 5.6: the visible base-to-apex height of 5.0-5.25 plus a small allowance for embedding, which also equals the apex height above water.
- Length vs width naming: the boat (length 10 = heading) and the eagle (length 0.8 = body) both move along X. So "length" is most likely the X extent, about 23.5.
  "Width" is then the Y extent (about 26-31). If the convention is instead max/min, width = 23.5. I propose 25.5, matching the family's own 43s/43/44 values of 25.5/24.8, which lies within about 10% of either reading.

## 4. Person speed

- 0027s (camera A): the feet track (frames 0-74, linear fit) is mapped to the ground in W. Ground speed is 1.34-1.62 m/s across pitch, f and ground height (central about 1.45).
  The walker moves mostly toward the camera. The image-plane-only speed is about 0.55, which is what the 0.57 answer corresponds to.
  The family stated value is 1.3 (same scripted walk, stated in 5 clips).
- 0022s: no person is visible in any frame. A component search outside the rock and boat found nothing.
  The only moving object is the boat (4 m/s). The answer 4.15 is a boat-like speed and is not a walking speed. The scene's walker is the same scripted 1.3 m/s.

## 5. Eagle wingspan (0023s)

- Camera C (0044) is the cleanest view. The wing axis (W Y) projects along image direction (-0.40, 0.92) at 18.6 px/m.
  That direction is nearly perpendicular to both the body axis and the image motion.
  The maximum spread per flap cycle is 37-42 px, which gives **2.0-2.2 m**.
- Camera B (0023): the wing axis is about 47 deg from the image plane (0.68 factor). The body and chord axis also project horizontally there, so the horizontal extent (45-52 px) includes the chord and body and overstates the span.
  My per-frame camera B values are 1.8-2.4 over most spread frames. They rise to 2.6 late in the clip, possibly from an attitude change.
- Family median is 1.98. The same eagle take in 0025s was answered 2.05. Proposed fix: 2.5 -> 2.05.

## 6. Proposed fixes (this item)

| qid | clip | q | current | new |
|---|---|---|---|---|
| 1668 | 22s | person walking speed | 4.15 | 1.3 |
| 1693 | 27s | person speed | 0.57 | 1.3 |
| 1670, 1680, 1690, 1696 | 22s/24s/27s/28s | rock length | 18.548 | 23.5 |
| 1682, 1692, 1698 | 24s/27s/28s | rock width | 10.0 / 8.5 / 8.8 | 25.5 |
| 1671, 1681, 1691, 1697 | 22s/24s/27s/28s | rock height | 7.8 / 7.78 | 5.6 |
| 1676 | 23s | eagle wingspan | 2.5 | 2.05 |

All other rows are kept. That covers boat heights and widths, the other wingspans, eagle speeds 1683/1743, rock width 1752 (25.5), and the stated facts.

## Notes for the p1 auditor (not my rows)

- 1116: 0027 "speed of the person from 1.0 s to 2.0 s" = 1.0. Same walker; my ground track gives 1.34-1.62 and the family value is 1.3.
- 1105: 0023 wingspan 2.5. Same issue as 1676.
- 1170/1171 (rock width 25.5/24.8) agree with this audit.
