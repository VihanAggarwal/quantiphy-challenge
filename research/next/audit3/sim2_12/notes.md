# Audit sim2_12: car family (simulation_0082/0083/0084) and classroom family (simulation_0229/0230)

Result: **no fixes proposed.** All 39 non-fact scored rows were checked; the 3 stated-fact rows (93, 100, 102) were left alone, and they are consistent with the measurements.
There are two open issues: the paper-plane depth (rows 720-723 vs 729-732) and the sign of the plane's acceleration. Neither meets the fix rule, but both are worth an orchestrator-level decision (see the end of this file).

Scripts are in this folder: cars*.py, crop.py, track_plane.py, planekin.py, ceil.py, cat.py, room.py.
Frames were read with OpenCV inside the scripts. Only the crops I viewed were saved as PNGs, and those were deleted at the end except stack0229.png.

## Family tables

### Cars: same Cybertruck-like model, nadir camera, three different takes and camera heights

| quantity | 0082 | 0083 | 0084 | consistent? |
|---|---|---|---|---|
| scale (px/m) | 53.49 (length prior) / 53.66 (5.07 m/s) | 47.34 | 46.92 (speed prior) / 46.75 (length) | the two priors agree within 0.4% in every clip |
| yellow width (mirrors) | 2.46 | 2.442 | 2.44 | yes |
| BW length | 5.65 | 5.67 | 5.66 | yes |
| BW width | 2.46 | 2.442 | 2.43 | yes |
| BW speed | 7.11 | 7.134 | 7.09 | yes (BW/yellow pixel-speed ratio is 1.398-1.399 in all three) |
| motion | both cars drive left (same direction) | opposite directions, separating | opposite directions, approaching | different takes, so the distances should differ |
| lateral offset dy | 2.61 m | 2.605 m | 2.38-2.40 m | 0084 is a different take or lane; my bbox check agrees (112.5 px / 46.95) |

### Classroom: same camera and same plane motion in both clips (plane pixel track identical, about 69.3 px/frame at frame 24); 0230 adds a cat

| quantity | 0229 | 0230 | note |
|---|---|---|---|
| board scale | 1370.5 px = 5 m | 1372 px = 5 m | I measure 1368 px (321-1690) |
| clock | 0.412 | 0.412 | 113 px |
| board height | 1.62 | 1.607 | 440-451 px, depending on whether the chalk tray is included |
| chair width | 0.50 | 0.515 | |
| teacher's table | 2.287 | 2.25 | 692-700 px at depth 0.895 |
| ceiling height | 2.837 | 2.85 | 174 to 951.5-957 px |
| plane v(1 s) | 6.07 | 5.45 | depth assumption: 0229 uses wall depth 1.0; 0230 uses an unmeasured 0.9 "hedge" |
| plane a(1 s) | 2.95 | 2.74 | |
| plane v(1.25 s) | 5.35 | 4.81 | |
| plane a(1.25 s) | 2.80 | 2.74 | |

## Row-by-row quick check

| qid | clip | quantity | current | quick check (independent route) | diff | verdict |
|---|---|---|---|---|---|---|
| 88 | 0082 | yellow width | 2.46 | mirror tips 334-466 px at f24 = 132 px / 53.49 = 2.47 | <1% | ok |
| 89 | 0082 | BW length | 5.65 | BW 1071-1375 = 304 px vs yellow 307 px at a larger off-axis offset: same model, so 5.65-5.67 | <1% | ok |
| 90 | 0082 | BW width | 2.46 | 474-606 = 132 px = 2.47 | <1% | ok |
| 91 | 0082 | distance at 1 s | 3.27 | centres f24: dx 105.5, dy 140, which gives 175.3 px = 3.28 | <1% | ok |
| 92 | 0082 | distance at 2 s | 4.78 | f48: dx 215, dy 140, which gives 256.6 px = 4.80 | <1% | ok |
| 93 | 0082 | yellow speed | 5.07 | stated fact; the pixel speed with the length scale gives 5.09 | - | fact |
| 94 | 0082 | BW speed | 7.11 | BW centre f24 to f48 = 381.5 px / 24 frames = 15.90 px/f, which gives 7.13 | <1% | ok |
| 95 | 0083 | yellow width | 2.442 | mirror span about 116 px / 47.34 = 2.45 | <1% | ok |
| 96 | 0083 | BW length | 5.67 | BW bbox 274 px vs yellow 276 px at a similar offset: same model | <1% | ok |
| 97 | 0083 | BW width | 2.442 | 116-118 px, which gives 2.45-2.49 | ≤2% | ok |
| 98 | 0083 | distance at 1 s | 10.348 | bbox centres f24: dx 467 px / 47.34 = 9.86, dy 2.605, so D = 10.20 | 1.5% | ok |
| 99 | 0083 | distance at 2 s | 22.399 | f48: dx 1041.5 px, which gives 22.0, so D = 22.15 | 1.1% | ok |
| 100 | 0083 | yellow speed | 5.07 | stated fact | - | fact |
| 101 | 0083 | BW speed | 7.134 | profile track 14.01 px/f × 24 / 47.34 = 7.10 | <1% | ok |
| 102 | 0084 | yellow length | 5.67 | stated fact; the speed-prior route gives 5.66 | - | fact |
| 103 | 0084 | yellow width | 2.44 | mirror tips 468-583 = 116 px / 46.95 = 2.47 | 1% | ok |
| 104 | 0084 | BW length | 5.66 | same model | <1% | ok |
| 105 | 0084 | BW width | 2.43 | 581-695 = 115 px, which gives 2.45 | 1% | ok |
| 106 | 0084 | distance at 1 s | 23.98 | bbox centres f24: dx 1111.5 px / 46.92 = 23.69, dy 2.40, so D = 23.81 | 0.7% | ok |
| 107 | 0084 | distance at 2 s | 11.95 | f48 crop: dx 549.5 px, which gives 11.71, so D = 11.96 | <1% | ok |
| 108 | 0084 | BW speed | 7.09 | profile track 13.92 px/f; ratio route gives 7.12, length-scale route 7.15 | ≤1% | ok |
| 715 / 724 | both | clock | 0.412 | 113 px × 5/1368 = 0.413 | <1% | ok |
| 716 / 725 | both | board height | 1.62 / 1.607 | 440-451 px, which gives 1.61-1.65 | ≤2% | ok |
| 717 / 726 | both | chair width | 0.50 / 0.515 | backrest 1600-1753 = 153 px at depth 0.897, which gives 0.50 (crop viewed) | ≤3% | ok |
| 718 / 727 | both | table length | 2.287 / 2.25 | top slab 75-775 = 700 px at depth 0.896, which gives 2.29 | ≤2% | ok |
| 719 / 728 | both | ceiling height | 2.837 / 2.85 | junction rows 174 and 951.5-957, so 777-783 px, which gives 2.84-2.86 | <1% | ok |
| 720 / 729 | both | plane v(1 s) | 6.07 / 5.45 | backward-difference blob track 69.3 px/f. At wall depth: 6.07. At depth 0.9: 5.46. At the ceiling-shadow depth 0.884: 5.36 | depends on depth | no fix (see below) |
| 721 / 730 | both | plane a(1 s) | 2.95 / 2.74 | d\|v\|/dt = -680 to -880 px/s² (mean about -790). Wall depth: -2.9; at 0.9: -2.6 | magnitude ≤12% | no fix; sign issue |
| 722 / 731 | both | plane v(1.25 s) | 5.35 / 4.81 | 61.2 px/f (raw backward difference 60.2-61.7). Wall depth: 5.36; at 0.9: 4.82; at 0.884: 4.74 | depends on depth | no fix |
| 723 / 732 | both | plane a(1.25 s) | 2.80 / 2.74 | -710 to -890 px/s². Wall depth: -2.95; at 0.9: -2.66 | magnitude ≤8% | no fix; sign issue |
| 733 | 0230 | cat length incl. tail | 0.66 | tail tip 162 to nose 350 = 188 px. Feet on the desk top (y about 737-740) give depth 0.967-0.98, so 0.00352-0.00357 m/px and 0.66-0.67 | ≤2% | ok |
| 734 | 0230 | cat height | 0.49 | tail top 596 to feet 740 = 139-144 px, which gives 0.49-0.51 | ≤4% | ok |
| 735 | 0230 | cat average speed | 0.756 | nose 350 to about 796 over 49 frames = 218 px/s, which gives 0.77 | 2% | ok |

The cat was isolated by differencing 0230 against 0229 frame by frame: the two clips are the same render apart from the cat.

## Open issue 1: paper-plane depth (rows 720-723 vs 729-732)

- Both clips show the same plane motion in pixels, so their labels should be identical. The current answers differ by about 11%, and the difference comes purely from the depth assumption: 0229 uses the wall/board depth (1.0), and 0230 uses 0.9, which its agent chose without measuring it ("hedged").
- Depth cues I tried:
  - No cast shadow on the board or wall.
  - No floor reflection is in view.
  - The brightness along the path shows no sun-beam signature.
  - The vertical acceleration at the apex is about 2360 px/s². That would be about 8.6 m/s² at wall depth, which is less than g, so the plane is not in free fall and gravity cannot set the scale. The path is keyframed or has lift.
- One weak cue was found. Stacking difference images in a frame that follows the plane shows a clear, elongated darkening on the ceiling, about 1.7 grey levels deep, at image y of about 126. It is reproducible in both clips and stays at a constant y while the plane's own y moves between 341 and 460. That suggests occlusion of floor-bounce light roughly vertically above the plane.
  - The ceiling point at y = 126 lies at Z/Zwall = 365.3 / (539.3 - 126) = 0.884. That gives v(1 s) = 5.36 and v(1.25 s) = 4.74.
  - If the bounce light comes mainly from the bright sunlit floor near the camera, the shadow is pushed toward the wall, which would make the plane even nearer to the camera.
- This is a single, model-dependent route, so it is not enough for a fix. Moving 0229 to the 0.884 estimate would also be only an 11-13% change, below the 15% threshold.
- **Suggestion (not a fix):** if the orchestrator wants the twin clips to agree, the 0230 values (5.45 / 4.81) are the better-supported pair. The 0229 values imply the plane flies exactly at the board plane, which the ceiling shadow argues against.

## Open issue 2: sign of the plane acceleration (rows 721, 723, 730, 732)

- The plane is clearly decelerating. Its backward-difference speed falls from 76.6 px/f (f17) to 58.8 px/f (f32), and d|v|/dt is about -790 px/s² at both 1 s and 1.25 s.
- The current answers are positive magnitudes (2.74-2.95).
- If the label really is the signed "change of speed magnitude per second", it is negative: about -2.6 to -2.9 m/s², depending on depth. A positive answer would then be about 200% off.
- I cannot settle the sign convention without labels, so I propose no change. This is a policy decision for the orchestrator, based on whatever sign evidence exists for decelerating objects elsewhere.
- For completeness: if the label were instead the full acceleration-vector magnitude, it would include the curvature of the arc. That gives \|a\| of about 9 m/s² at wall depth, so it is not consistent with "change of speed".

## Other caveats (no action)

- **Car widths (88, 90, 95, 97, 103, 105).** All three agents measured independently and got 2.43-2.46 m, mirror tip to mirror tip, which matches the real Cybertruck with mirrors (2.41 m). If the ground-truth box excludes the mirrors, the answer would be about 2.0-2.1 m. Nothing in the frames can settle this, and the mirrors are painted in body colour, so they are probably part of the same mesh.
- **Car distances.** These assume the origin is at the bbox centre and t = frame_index / fps (1 s = frame 24). A one-frame shift changes 0083 and 0084 by about 0.5 m: 5% for row 98 and 4% for row 107.
