# Lab audit round 2: family 0040 (captured_0040, 0040s, 0040x)

The three renders show one event and share labels. Every scored row is S3. Round 1 made no changes
(research/next/labaudit/0040/notes.md). I reused the round-1 frame PNGs and wrote new scripts in `scripts/`.

## Result

One fix, applied to all three renders: **v(1.5 s) of the white ball goes from 106.08 to 82.0 cm/s** (qids 2742, 2750, 2758).

There is one near-miss that I did not fix:

- **v(1.4 s)** (qids 2748, 2756, 2764): 106.08 is 15-23 % below my label-style value of 125-141 cm/s.
- That misses the 25 % bar.
- An answer of about 130 cm/s scores higher in expected MRA under every noise level tested (see below).

All other rows stay as they are.

## Time base: the dropped capture frame is after video frame 35

Video frame n maps to capture frame c(n) = n + (n>=12) + (n>=36), on a 25 fps clock.

Evidence:

1. **Horizontal image steps.** Video steps 33→34 to 39→40 are 33.6, 30.3, **61.5**, 32.3, 34.6, 34.3 and 32.2 px.
   Only 35→36 is double length.
2. **Ballistic fit, video frames 34-40, g = 9.8 along the table normal, depth left free** (`scripts/drop_check.py`):

   | time base | rms (px) | range at video 36 (m) |
   |---|---|---|
   | 25 fps, drop after video 35 | 1.2-1.5 | 0.73 |
   | 25 fps, drop after 34, 36 or 37 | 7-9.5 | 0.65-0.78 |
   | 24 fps or 25 fps, no drop | 4.4-5.1 | 0.51-0.56 |

   With the drop after 35, the fitted range matches the stated surface range plus the 2 cm ball radius (0.7045 + 0.02 = 0.7245 m).
   This also explains round 1's "implied g of 7.4-8.1": round 1 used the 24 fps clock without the drop.

The question time t=1.5 s corresponds to video frame 36, which is capture frame 38 (1.52 s). The forward difference is therefore capture 38→39, which is video 36→37.

Two checks support this:
- Rounding capture frame 37.5 to the nearest frame also gives 38.
- The stated depth at 1.5 s (0.7045) is closer to the ballistic surface range at c38 (0.711) than at c37 (0.724).

t=1.4 s is capture frame 35 under both conventions, so its forward difference is c35→36 (video 34→35).

## Clicked centres

- **Clean frames:** blob centroid.
- **Frames 32, 34, 35 and 38**, where the SAM2 compositing draws the tape, card tower or cup over part of the ball: I fitted a capsule (a motion-blurred disc) to the blob edges that border empty background.
  - For frame 34 I fixed the axis, half-length and radius from the neighbouring frames (`scripts/track_capsule.py`, `capsule_fixed.py`, images in `img/capfit_*`).
  - On clean frames the capsule centre agrees with the centroid to within 1 px.
- The x and s renders agree to within 0.5 px.
- **Ballistic fit through video frames 35-39 (capsule centres):** rms 0.4 px. Frame 34, which was left out of the fit, sits within about 1.5 px of the fitted curve.

## Motion rows

Scripts: `scripts/motion.py` (label-style), `ballistic25.py` (physical) and `candidates.py` / `noise_opt.py` (expected MRA under the research/labnoise label-noise model). All speeds are in cm/s on the 25 fps clock.

| row | current | label-style FD, stated-depth route | label-style FD, size-depth route | ballistic g=9.8 (FD on curve / instantaneous) | verdict |
|---|---|---|---|---|---|
| v(1.5) = c38→39 | 106.08 | 77.1-79.0 (x, s; centroid or capsule) | 71.1-73.1 | FD 79.8-87.7 (mean 83.4); instantaneous at c38 81-89, at c37.5 87-95 | **fix → 82.0** |
| v(1.4) = c35→36 | 106.08 | 125 (capsule) / 137 (centroid) | 115-129 | FD 137-148; instantaneous at c35 154-165 | near-miss, no fix |
| path 1.5→1.9 s = c38..48 | 39.81 / 39.81 / 39.48 | 38.0 | 36.9 | (crosses the c43 bounce) | ok, within 5 % |

### Why 106.08 is wrong at 1.5 s

The current value is Claude's direct answer of 92 cm/s times the labnoise factor 1.153. Claude gave the same 92 for t=1.4 s and for t=1.5 s.

At t=1.5 s the ball is at the apex of its hop over the cup rim:
- The apex is at capture frame 38.3.
- The image step c38→39 is 32 px, almost all horizontal.
- The ball is about 0.70 m from the camera.

Those numbers give about 78-80 cm/s from the stated depths and about 83 cm/s from the gravity-scaled ballistic fit. The speed 0.1 s earlier is 1.7 times higher.

The decision criteria are met:

| criterion | evidence |
|---|---|
| (a) two routes agree within 12 % | stated-depth track FD (77-79) and ballistic g=9.8 FD (83.4); the two depth sources are independent |
| (b) current off by at least 25 % | 106 is +29 % against 82 and +34-38 % against 77-79 |

### Choice of 82

82 is a value between the label-style forward differences (77-81, using surface ranges) and the physical speed (about 85). It is rounded up slightly for the noise inflation of slow labels.

Expected MRA from `candidates.py`, by the true value and the ToF noise σ_z (in m):

| answer | true 77 cm/s, σ_z = 0 / 0.01 / 0.02 / 0.03 | true 82.5 cm/s, σ_z = 0 / 0.01 / 0.02 / 0.03 |
|---|---|---|
| 82 | .88 / .86 / .77 / .68 | .90 / .86 / .76 / .67 |
| 106 | .57 / .66 / .71 / .69 | .66 / .73 / .75 / .71 |

82 is better than 106 everywhere except at σ_z = 0.03, where the two are within .02.

### v(1.4) near-miss

| quantity | value (cm/s) |
|---|---|
| label-style, from my tracks | 125-138 |
| ballistic FD with surface ranges | 133-144 |
| physical speed at 1.40 s | 154-165 |

106 is 15-23 % below the label-style range, which misses the 25 % bar, so it is left as is. In expected MRA:

| answer | σ_z = 0 | σ_z = 0.02 |
|---|---|---|
| 106 | .70-.80 | .64-.71 |
| 130 | .89-.92 | .80-.86 |

The orchestrator can adopt 130 for qids 2748, 2756 and 2764 if it relaxes the bar.

### Path

The noiseless sum of forward differences over c38..48 is 37-38 cm. Shifting the window by half a frame at either end gives 34.5-41.5 cm. The current 39.8 / 39.5 is within that range and needs no change.

## Static rows (re-checked; `scripts/static_check.py`, `img/static_zoom.png`)

| row | current (o / s / x) | my value at stated range | verdict |
|---|---|---|---|
| poker tower height | 10.42 / 10.34 / 10.25 | 82 px → 10.5 | ok |
| cup rim diameter | 9.00 / 8.48 / 8.48 | 73-75 px → 8.3-8.55 at 0.842 m, 8.8 at silhouette depth | ok, all within 6 % |
| white ball diameter | 4.0 | 4.0 | ok |
| tape diameter | 10.47 / 10.46 / 10.47 | 78.3 px → 10.7 | ok |
| cup height | 14.82 / 14.73 / 14.73 | 127 px → 14.9 | ok |

How the ball diameter is confirmed:
- The ball size and the stated ranges give 4.0 cm.
- The ballistic fit at g=9.8 gives a range of 0.73 m, which matches the size-based range for a 4 cm ball.

The stated cup range "8420m" is a typo for 0.842 m. The current answers do not use the typo value.
