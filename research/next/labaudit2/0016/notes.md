# Lab audit round 2: family 0016 (captured_0016, 0016s, 0016x). One event, one label set.

Inputs: `../inputs/0016.json`, 12 scored rows (4 questions x 3 renders), all D3. There are no S3 rows.
- No labels were used.
- No prior in the test split states this ball's size. The clip's only prior is g = 9.8 m/s^2.
- Round 1 (`research/next/labaudit/0016/notes.md`) changed nothing. I reused its frame PNGs read-only; no frames were dumped.
- Scripts are in `scripts/`, crops in `img/`.

Camera: f = 711, principal point (640, 360). R = ball radius.

## Clock: one dropped capture frame after video 35 (confirmed)

**Image steps (`track.py`).** x-render matte centroids, video 32-40:

| video | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| x (px) | 586.8 | 640.8 | 688.7 | 735.2 | 812.2 | 844.7 | 872.3 | 894.5 | 913.1 |
| y (px) | 256.2 | 198.8 | 156.0 | 121.1 | 77.2 | 70.3 | 70.5 | 77.3 | 90.6 |

- The dx steps are 54, 48, 46.5, **77**, 32.5, 27.6, 22.2, 18.6. The bold step is two steps of about 41 and 36.

**Ballistic fit (`dropcheck.py`).** Image-only, |g| = 9.8, gravity direction free, video 33-40:

| time base | rms (px) |
|---|---|
| drop after video 35 | **0.44** |
| no drop | 5.1 |
| 24 fps | 5.3 |
| drop after 33 / 34 / 36 / 37 | 7-8.6 |

- Mapping: capture n = k + (k>=12) + (k>=36). This is the same pattern as in 0028, 0035 and 0040. The drop after 11 cannot be seen because the ball is held, and the results do not depend on it.
- Times:
  - t = 1.0 s is capture 25 = video 24.
  - t = 1.5 s is capture 37.5. Capture 37 is the missing frame, and capture 38 = video 36.
  - Both conventions were carried through: **A** = c38->c39 (video 36->37), **B** = c37->c38.

**Gravity direction, two independent routes that agree:**
- **Size route (`fit3d.py`):** centroid plus the matte extent perpendicular to the motion, inverted with the sphere-silhouette model. A 3D quadratic over video 36-40 has rms 0.05-0.27 cm, giving pitch 32.4 deg and roll -19.5 deg.
- **Image-only ballistic:** pitch 31-32 deg, roll -16 deg.
- Round 1's "45-55 deg pitch, roll 0" was wrong. The vertical vanishing point is at about (270, 1410), which matches both the far person's and the near person's body axes.

**Depth consistency.** The image-only ballistic fit, with no anchor and f = 711, gives a surface range of 1.428 at c37 and 1.493 at c38. The stated value is 1.402, so it matches c37 (+2%) better than c38 (+6.5%). With the f/ToF scale uncertainty this does not decide between A and B.

## Motion rows

### v(1.5 s) (qids 2283 / 2287 / 2291; current 2.27 / 2.48 / 2.44 m/s)

**Label-style values** (`ballistic.py`, `fit3d.py`, `labelstyle.py`):
- **Ballistic, gravity free, 33-40:**
  - A = 2.31 (no anchor), 2.41 (anchor 1.402 at c38).
  - B = 2.42 (no anchor), 2.41 (anchor at c37).
- **Ballistic, gravity fixed to the size-route direction:**
  - A = 1.98-2.34.
  - B = 2.12-2.45.
- **Size route scaled to the stated anchor:**
  - A = 2.08 (anchor c38, implied D = 17.0).
  - B = 2.27 (anchor c37, D = 17.7).

**Physical speed:** |v(c37.5)| = 2.26-2.55, and |v(c38)| = 2.19-2.48.

**Sensitivity.** The label depends mostly on the unknown next ToF reading:
- In A, r39 = 1.44 / 1.46 / 1.48 / 1.50 gives 1.71 / 2.04 / 2.42 / 2.85. That is about 0.2 m/s per cm.
- The routes put r39 at 1.46-1.48.

**MC (`mc.py`).** Click sigma 2-3 px, ToF sigma 1-3 cm:
- Medians are A 2.05-2.44 and B 2.33-2.69.
- The interquartile range (IQR) is about ±0.3.

**Verdict: leave.** Current values are within -10% to +20% of every central estimate, and no route gets near the 25% bar.

### Displacement 1.0 -> 1.5 s (qids 2284 / 2288 / 2292; current 134.7 / 139.7 / 134.0 cm)

**Click at video 24.** The held ball is at (285, 597).

**r24 from the sphere edge fit (`edgefit.py`).** I used the unoccluded edge sectors.
- The tangential diameter at video 24 is 81-87 px, which is about the same as the 87 px at video 37.
- With the D implied by each anchor this gives:
  - A: r24 = 1.55-1.65 (D = 17.0).
  - B: r24 = 1.61-1.72 (D = 17.7).
- Round 1's r24 of about 1.48 was low. It does not matter much, because the displacement changes only about 0.6 cm per 1 cm of r24.

**Label-style displacement (`disp.py`):**
- A: 136-142.
- B: 132-139.

**Verdict: leave** (within about 5%).

## Static rows

### Distance between the two people (2281 / 2285 / 2289; current 225.2 / 224.3 / 224.5)
- `people.py`: 36 click pairs back-projected at near 0.843 and far 2.372 give 207-237, with median 224.1. Torso to torso is 225.5.
- This matches round 1's 222-226.
- **Verdict: OK.**

### Soccer ball diameter (2282 / 2286 / 2290; current 18.36 / 19.0 / 18.45)
Routes (`diam.py`):

| route | D (cm) |
|---|---|
| Sphere model with the stated range at c38 | 17.0 |
| Sphere model with the stated range at c37 | 17.7 |
| Image-only ballistic depth (no stated depth) with the matte size | 18.1 |
| \|g\| = 9.8 scaling of the size-route track | 19.1-19.3 |
| Label-style edge clicks at 1.402, by click direction (perp 92.9 px / blurred horizontal 118 px) | 15.5-20.5 |
| Prop transfer (0034/0035, from other notes) | 17.8 |
| 0054 | 18.7-19.4 |

- The current values are +4% to +12% against the 17.0-18.1 cluster and inside the full 17-19.3 band.
- **Verdict: OK.** No route pair within 6% puts the current answer 12% or more off.

## Result
**No fixes.** All 12 rows stay as they are.

The closest call is v(1.5) on o (2.27) versus s/x (2.44-2.48). Every one is within 20% of the label-style band of 2.0-2.7, and that band is dominated by the unknown next-frame ToF reading, at about 0.2 m/s per cm.
