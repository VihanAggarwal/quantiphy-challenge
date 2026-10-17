# Audit sim2_22: simulation_0127, 0197, 0200, 0203, 0207

Inputs: research/next/audit3/inputs/sim2_22.json (41 scored rows) and the five agent notes.md files it lists.
No labels or validation data were opened. Frames were read with OpenCV inside scripts. Only small PNG crops were kept.

## Family structure (from inspecting the frames)
- 0203 and 0207 are the SAME desk scene with the SAME camera (lamp, clock, phone, papers at identical pixels).
  0203: magnifying glass falls at centre, typewriter at rest on the left with a sheet in it.
  0207: typewriter falls at centre, and the sheet stands alone where the typewriter was. Shared objects must have the same sizes.
- 0197 and 0200 show the same "SKYNOVA" dropper-bottle asset (same proportions: pipette tube/body = 0.19 in both),
  but with a different camera and background (0200 has a plinth). The input lists them as separate families.
- 0127 (top-down street) is on its own.

## Scene geometry used for 0203/0207 (level camera)
- Table side edges meet at horizon y_h = 546.6, VP x ~1066-1070 (both agents agree, independently). Table width W(y) = 3.796*(y - y_h).
- Glass fall (0203): centroid parabola a = 12.99 px/f^2 (max residual 0.7 px), vertex -0.03 f, so s_glass = 1.310e-3 m/px.
  The landed ring has 108 px major axis (in air: 103-105 px, same depth). Its contact-row centre is 1018.5, so h = 0.618 m.
- Typewriter fall (0207): paper-rest-bar template a = 12.03 px/f^2 (res 0.5 px), vertex -0.24 f, so s_bars = 1.414e-3.
  Front-bottom-edge pixel velocity (frames 7-8) is 1.09x the bar velocity, so s_fb = 1.30e-3. With the landed front-bottom
  row of ~1019-1022, this gives h = 0.612-0.62 (independent of the glass route).
  The in-air silhouette extent stays constant above eye level (126 px), so the back-bottom edge is at the same depth as the bars.

## Row table (current, quick check, verdict)
| qid | clip | quantity | current | quick check (route) | verdict |
|---|---|---|---|---|---|
| 287 | 0127 | blue car v(1.0s) | 19.3 | car rear edge 25.21 px/f vs bike 31.0-31.5 px/f -> 19.2-19.5 | ok |
| 288 | 0127 | blue car width | 2.95 | body ~88 / mirrors ~96 px x 0.032 -> 2.83-3.07 | ok (hedge) |
| 289 | 0127 | blue car length | 7.6 | ~241 px -> 7.6-7.7 | ok |
| 290 | 0127 | bike length | 2.71 | ~86 px (f30) -> 2.72-2.75 | ok |
| 291 | 0127 | red car width | 2.96 | body 717-806 (89 px), mirrors ~98 -> 2.85-3.1 | ok |
| 292 | 0127 | red car length | 7.6 | 14->256 (242 px) -> 7.6-7.74 | ok |
| 293 | 0127 | green car width | 3.07 | 92-100 ground px -> 2.94-3.2 | ok |
| 294 | 0127 | green car length | 7.14 | 1686->1916 (230 px), edge perspective -> 7.0-7.36 | ok |
| 497 | 0197 | plunge tube diam | 0.0051 | ~216 px perpendicular x 2.35e-5 -> 0.0051 | ok |
| 498 | 0197 | droplet width | 0.0026 | ~108 px -> 0.0025 | ok |
| 499 | 0197 | lettering vertical height | 0.0232 | letter runs A 2035-2159, V 2171-2295, O 2311-2439, N 2474+; word ~965-1020 px -> 0.0227-0.024 | ok |
| 500 | 0197 | neck diam | 0.0172 | threads 700 / flange 771 px -> 0.0165-0.0181 | ok |
| 501 | 0197 | body diam | 0.0273 | 1148-1178 px (rows 1990-2470) -> 0.027-0.0277 | ok (see caveat) |
| 502 | 0197 | bubble v(0.5s) | 0.0076 | bubble template track 10.7 px/f -> 0.0075 | ok |
| 503 | 0197 | bubble v(0.8s) | 0.0088 | 12.9 px/f -> 0.0091 | ok |
| 504 | 0197 | bubble v(1.0s) | 0.0087 | 12.2 px/f -> 0.0086 | ok |
| 523 | 0200 | droplet height | 0.0077 | 82-86 px x 9.29e-5 -> 0.0076-0.0080 | ok |
| 524 | 0200 | droplet horiz length | 0.00496 | 52-55 px -> 0.0048-0.0051 | ok |
| 525 | 0200 | neck diam | 0.0223 | 235-250 px -> 0.0218-0.0232 | ok |
| 526 | 0200 | body diam | 0.0333 | 353-368 px -> 0.0328-0.0342 | ok |
| 527 | 0200 | lettering height | 0.0251 | 683-951 = 268 px -> 0.0249 | ok |
| 528 | 0200 | v(0.2s) | 1.86 | 2nd diff ~29 px/f^2; frame-12 diff extrapolated ~333 px/f -> 1.86 | ok |
| 529 | 0200 | v(0.05s) | 0.41 | top-edge diff 74 px/f -> 0.412 | ok |
| 530 | 0200 | v(0.1s) | 0.895 | 161 px/f -> 0.897 | ok |
| 531 | 0203 | table length | 2.34 | 3.796*h, h=0.618 -> 2.35 | ok |
| 532 | 0203 | typewriter length | 0.395 | rest 305-315 px x s(1035)=1.265e-3 -> 0.386-0.40; 0207 in-air base 295 px x s_fb -> 0.384 | ok |
| 533 | 0203 | typewriter height | 0.20 | 0207 in-air 126 px x s_bars = 0.178; frames 7-8 -> 0.176-0.178; eye-level frame 6 -> 0.170; 0203 rest geometry consistent with ~0.17-0.18 | +13.6% vs 0.176, below 15% threshold, NOT proposed (harmonization candidate: 0.176 = sibling 548) |
| 534 | 0203 | paper width (next to glass) | 0.205 | back card visible x-extent 0.2045; front-left sheet AABB-x 0.212; standing sheet 0.196 | ok |
| 535 | 0203 | letter under gun length | 0.276 | world-corner AABB x 0.265 (h=0.62) to 0.271 (h=0.633) | ok |
| 536 | 0203 | glass v(0.125s) | 1.03 | 9.8*(2.5+0.03)/24 = 1.033 | ok |
| 537 | 0203 | glass v(0.25s) | 2.25 | 2.258 | ok |
| 538 | 0203 | glass v(0.333s) | 3.07 | 3.075 | ok |
| 546 | 0207 | table length | 2.42 | 2.35 (h=0.612-0.62) | ok (+3%) |
| 547 | 0207 | typewriter length | 0.388 | 0.384-0.39 | ok |
| 548 | 0207 | typewriter height | 0.176 | 0.170-0.178 | ok |
| 549 | 0207 | paper width (next to typewriter) | 0.27 | front-left sheet AABB-x 0.210-0.212 (both h routes); every paper candidate in the scene is 0.196-0.212 wide | **FIX -> 0.21** |
| 550 | 0207 | letter under gun length | 0.27 | 0.265-0.271 | ok |
| 551 | 0207 | typewriter v(0.125s) | 1.09 | bars parabola, vertex -0.24 f -> 1.12 (raw diff 1.13) | ok (3%) |
| 552 | 0207 | typewriter v(0.25s) | 2.32 | 2.345 | ok |
| 553 | 0207 | typewriter v(0.333s) | 3.13 | 3.16 | ok |

## Fix
**qid 549 (simulation_0207, width of the paper next to the typewriter): 0.27 -> 0.21**
- The landed typewriter sits right next to the flat front-left sheet. Its image corners are FL(732,1042), BL(744,1000),
  BR(884,997) and FR(884,1041). On the table plane, X = (x-1066)*h/(y-546.6), which gives world X of -0.418, -0.440, -0.251 and -0.228.
  The sheet is rotated about 4.5 deg. AABB x = 0.212 (short side 0.19).
  - Route 1: h from the typewriter's own fall (front-bottom-edge scale plus landing row): h = 0.612-0.62, so 0.210-0.212.
  - Route 2: h from the 0203 glass fall plus ring contact row: h = 0.618, so 0.211.
  - Corroboration: the other paper candidates are the back card (visible x-extent 0.205) and the standing sheet (0.196).
    In the sibling clip 0203, an independent agent answered the analogous question with 0.205.
- Why the current value is wrong: the agent measured x of about 0.225, using h = 0.637, which was inferred by assuming the
  tracked origin sits at the footprint centre 0.175 m behind the front edge. It measured the depth (y) extent as 0.30-0.32,
  which depends on f. It then hedged at the midpoint, 0.27. In these 2D-sim questions a flat sheet's "width" is its
  side-to-side (x) extent (as with "length of the letter" = x-extent 0.27, and the cars' widths), so the hedge sits about 28% above it.
- Risk: if the dataset meant the sheet's depth dimension (about 0.30), 0.21 would be 30% low. I judge that less likely.

## Caveats / not proposed
- 533 (0203 typewriter height 0.20) is 13.6% above my estimate and the sibling's 0.176. It is below the 15% bar, so it is not proposed.
  Harmonizing it to 0.176 would be a reasonable low-risk consistency change if the orchestrator wants sibling consistency.
- 0197 vs 0200 (same bottle asset): applying the 0200 droplet scale to the bottle gives body 33.3 mm, or about 35 mm if the
  pipette tip sits about 2 cm nearer the camera, as the cap orientation suggests. 0197's text-prior scale gives 27.3 mm.
  The lettering lengths differ by about 7% (23.2 vs 24.9 mm). Under the reading "prior = world x-extent of the text,
  camera axis-aligned", perspective cancels and 27.1-27.5 mm is exact. Under "projected extent at the text depth", the body
  would be about 31 mm. A camera yaw of about 8 deg relative to the world would give about 33 mm. The prior's
  semantics/azimuth cannot be resolved from the frames, and the input lists the clips as separate families, so no
  0197/0200 change is proposed. The risk on 0197 sizes is +10-20%.
- 0200 bottle sizes use the droplet-depth scale. The tip is probably a few cm nearer the camera than the bottle axis, so
  those sizes may be up to about 7% low. That is below threshold.
