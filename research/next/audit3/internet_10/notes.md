# Audit internet_10 (clips internet_0024, 0046, 0054, 0060, 0063)

All 30 rows are scored, and I checked all of them. Every family has one clip, so there are no twins to compare.
One cross-clip link exists: 0060 and 0063 show the same wall, black baseboard and wood floor, filmed by the same camera.
The baseboard band is 137-139 px wide in both clips, so the camera-to-wall distance is the same within about 1.5%.
Both objects also land at the same place relative to the band. So their g-derived scales should match within a few %.
Scripts are in work/. I deleted the PNG crops after viewing them.

## Quick-check table

| qid | clip | quantity | current | quick check (route) | diff | verdict |
|---|---|---|---|---|---|---|
| 2121 | 0024 | case length mm | 53 | case minAreaRect 224x199 px -> 50.7 mm (agent GrabCut 230x197 -> 52.5) | 4% | ok |
| 2122 | 0024 | pencil cm | 17.6 | 749 px end-to-end x 0.228 mm/px = 17.1 | 3% | ok |
| 2123 | 0024 | mug diameter cm | 9.6 | rim ~432-440 px -> 9.8-10.0 (top-down; rim higher than table) | 3% | ok |
| 2124 | 0024 | laptop long side cm | 32.5 | 1424 px -> 32.2-32.5 (matches MacBook Air 13" spec) | 0% | ok |
| 2125 | 0024 | wallet long side cm | 17.3 | ~760 px -> 17.2-17.4 | 0% | ok |
| 2126 | 0024 | mug v(0.50 s) cm/s | 36 | template match 12->13 = 64.4 px/fr, coffee centroid 64.6 -> 36.8 at table scale (about 33 at mug depth, since the lifted mug is about 7-12% larger) | 2-9% | ok |
| 3090 | 0046 | v(1.00) m/s | 0.54 | body-edge midpoint track, central diff 98.25 px/fr x 30 x 1.842e-4 = 0.543 | 0% | ok |
| 3091 | 0046 | v(1.10) | 0.62 | 112.75 px/fr -> 0.623 | 0% | ok |
| 3092 | 0046 | v(1.20) | 0.685 | 125.5 px/fr -> 0.694 | 1% | ok |
| 3093 | 0046 | disp 1.0-1.1 cm | 5.84 | 317.5 px -> 5.85 | 0% | ok |
| 3094 | 0046 | disp 1.1-1.3 cm | 13.65 | 744 px -> 13.70 | 0% | ok |
| 3095 | 0046 | a(1.10) m/s^2 | 0.70 | local quadratic over fr 30-36 gives 0.80; global fit 0.63 | +/-12% | ok (noisy) |
| 3145 | 0054 | person height m | 1.624 | 289 px x (4.9/497) = **2.85** | 43% | **fix (convention)** |
| 3146 | 0054 | bench length m | 1.589 | 278 px -> **2.74** (2D) | 42% | **fix (convention)** |
| 3147 | 0054 | canopy height m | 3.364 | 585 px (top of foliage to ground) -> **5.77** | 42% | **fix (convention)** |
| 3148 | 0054 | canopy width m | 10.506 | 1838 px -> **18.1** | 42% | **fix (convention)** |
| 3149 | 0054 | scooter height m | 1.087 | 186-190 px -> **1.85** | 41% | **fix (convention)** |
| 3150 | 0054 | wheel-to-wheel m | 0.964 | outer 181 px -> 1.78, axle 142 px -> 1.40; hedge **1.6** | 40% | **fix (convention)** |
| 3189 | 0060 | box length cm | 8.8 | 104 px / 1117 px/m (0063 transfer) = 9.3 | 5% | ok |
| 3190 | 0060 | box width cm | 8.3 | 98 px / 1117 = 8.8 | 6% | ok |
| 3191 | 0060 | box-floor dist t=0 m | 1.12 | 1298 px / 1117 = 1.16 | 4% | ok |
| 3192 | 0060 | v(2.00) m/s | 2.78 | 111-112 px/fr (all fits agree) x 30.01 / 1117 = 2.99 | 7% | ok |
| 3193 | 0060 | disp 0-2 s m | 0.46 | 534 px / 1117 = 0.48 | 4% | ok |
| 3194 | 0060 | disp 2.2-3.0 s m | 0.29 | ~320-332 px / 1117 = 0.29-0.30 | 2% | ok |
| 3207 | 0063 | bottle height cm | 24.2 | 256 px / 1117 = 22.9 | 5% | ok |
| 3208 | 0063 | bottle diameter cm | 6.5 | 69 px / 1117 = 6.2 | 5% | ok |
| 3209 | 0063 | v(1.50) m/s | 1.89 | leading-edge free fall g(t-t0), t0 = 39.67 fr -> 1.75 (centroid fit gives 1.90) | 8% | ok |
| 3210 | 0063 | v(1.70) m/s | 3.87 | 3.71 (leading edge) to 3.8 (centroid) | 4% | ok |
| 3211 | 0063 | disp 1.5-1.7 m | 0.573 | 0.546 (free fall from leading-edge t0) | 5% | ok |
| 3212 | 0063 | bottom-floor dist 1.5 s m | 0.866 | (1470-1480 - 562 px)/1117 = 0.82; free fall to impact at fr 53.05 = 0.818 | 6% | ok |

## Notes per clip

- **0063 scale.** The bottle's leading edge (bottom) fits a pure parabola: g = 12.05-12.25 px/fr^2 with rms 0.3-0.6 px, and a drag
  term does not improve the fit. That gives 1117 px/m, versus the agent's 1056 (centroid). Every 0063 row is within 8%, so there is no fix.
- **0060 scale.** The box (a light paper medicine box) slows down clearly. A drag fit gives g = 13.0 px/fr^2 with rms 0.53 px; a plain
  parabola gives 11.2 with rms 2.35. The bottle in 0063 shows no slow-down, and it was filmed by the same camera over a similar x
  range. So rolling shutter and lens distortion do not explain the slow-down, and the drag is real. The agent's scale is 1190 px/m;
  the scale carried over from 0063 is 1117 px/m. These two routes agree within 6.5%, and every 0060 row is within 8% of the
  transfer route. There is no fix. The plain quadratic (1010 px/m) would move the size rows about 15% and is rejected.
- **0046.** My track reproduces the agent's numbers to within 1% (camera static; cup height 570 px = 10.5 cm). Acceleration is noisy
  (0.63-0.80), and 0.70 sits in the middle.
- **0024.** Every size row is within 4%. The mug is lifted toward the camera at t = 0.5 s, so a depth-correct speed would be about
  33 cm/s, against 36.8 at table scale. The current 36 is fine under either convention.
- **0054 (only flagged clip).** The rider moves 16.53-16.60 px/frame relative to the scene. Template track minus bench-depth shift:
  496 px/s. Shirt-blob centroid minus building shift: 501 px/s. The steps are uniform from frame to frame, so there is no sign of 50->30
  frame dropping. The stated 4.9 m/s therefore gives 0.00986 m/px, and the agent used the same scale (0.0099).
  The current answers come from an older pipeline and use 0.00578 m/px. That implies a rider speed of about 2.9 m/s, not 4.9.
  Rows 3146 and 3150 equal the agent's value times 1.665/2.85 exactly, which means the old pipeline rescaled the clip so the person is
  1.665 m tall: a world-knowledge invariant overriding the stated prior. Under the audit rule ("the stated prior is exactly true and
  sets the scale"), every 0054 row is about 1.7x too small, so I propose restoring the prior-scaled values.
  **Caveat:** with the prior scale, the real-world sizes are implausible (person 2.85 m, bench 2.7 m, scooter 1.85 m tall). A scooter
  of about 1.1 m and a person of about 1.7 m would both put the real scale at about 0.0059 m/px. 4.9 m/s is also 11 mph, and
  2.95 m/s x 50/30 = 4.9. So the speed prior may come from a speedometer reading or a wrong fps, with ground truth in real-world sizes.
  If the team has evidence that the person-height invariant is validated for internet speed priors, reject these six fixes.
  Depth: the bench and canopy stand about 12-29% farther away than the rider (ground rows 1087 vs 1127). I give 2D values, as the
  agent did. A depth-correct bench under the prior convention would be about 3.1-3.5 m.
  Canopy height: 585 px counts the foliage on top. The bare structure (beam) would be about 443 px, which gives 4.4 m.
  Wheel-to-wheel: 181 px measured over the outer edges of both wheels, 142 px measured axle to axle. I hedge at 1.6 m.

## Proposed fixes (all in 0054, and all depend on the convention above)

| qid | current | new | routes |
|---|---|---|---|
| 3145 | 1.624 | 2.85 | rider speed 496/501 px/s (2 tracks); person 289 px (mine) / 288 (agent) |
| 3146 | 1.589 | 2.74 | bench 276-280 px (mine, 4 benches) / 275 (agent) |
| 3147 | 3.364 | 5.77 | 585 px (mine) / 586 (agent) |
| 3148 | 10.506 | 18.1 | 1838 px (mine) / 1840 (agent) |
| 3149 | 1.087 | 1.85 | 186-190 px (mine) / 190 (agent) |
| 3150 | 0.964 | 1.6 | outer 181 / axle 142 px (mine), 181 / 143 (agent); hedge |
