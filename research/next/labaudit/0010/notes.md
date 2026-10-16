# Lab audit, family 0010 (captured_0010 / 0010s / 0010X): one event, one label set

Scene: a person holds a string with the red ball (same person, same red ball and string as captured_0027, whose
prior gives the red ball as 7 cm). The pendulum swings mostly toward and away from the camera. Clips have 49 frames at
24 fps (2.0 s). The 's' render (green background) gives a clean ball mask, so all tracking uses it. The X render loses
the ball colour after frame 11. The original render is blurred, but the hand and string are visible in it.
Prior: g = 9.8. The stated ranges are on a 0.3 s grid: 1.706, 1.344, 1.4605, 1.784, 1.717 and 1.350 m at t = 0.3 to 1.8 s.

Scripts: scripts/extract.py (frames), scripts/track3d.py (mask centroid, Dx = 4*std_x as a blur-robust diameter),
scripts/fit.py (harmonic 3D model, circle and ray pivot fits), scripts/hyp.py (chord hypotheses with the stated ranges),
scripts/pendfit.py (full 3D pendulum fit to u, v and size). Images: montage_*.png, crops_s.png, crops_o.png,
ref_0027_f5.png.

## Ball diameter (2192/2198/2204, current 7.0): OK
- Route 1, size x stated range / f (f = 711): 7.01, 6.93, 6.90, 7.19, 7.41 and 6.77 cm at the six stated times
  (mean 7.04). The integer bbox widths give the same about 7.0.
- Route 2, identity: the same red ball on a string as in 0027 (ref_0027_f5.png), whose prior states 7 cm.
- Range check: the size-implied range divided by the stated range gives ratios of 0.97 to 1.06 (mean 1.005), so the
  stated ranges and D = 7 cm agree.

## String length (2191/2197/2203, current 35.0): OK, within the convention ambiguity
- Pivot (the string top under the hand) is at about pixel (639, 226) in the s render, frames 12, 17 and 46.
- Route 1, ray-constrained pivot: put the pivot on that ray and choose its depth so the ball stays at a constant
  distance. Pivot to ball centre comes out 0.331 to 0.353 m for a pivot y of 232 to 220 px.
  Two-extreme closed form (frames 3 and 17): 0.338 m.
- Route 2, period: the turning points from u and size extrema are 29.5 to 30 frames apart, so T is about 1.23 s.
  The full pendulum fit gives T = 1.205 s. With an amplitude correction for theta0 of 38 to 50 deg, L is 0.33 to 0.36 m.
- So pivot to ball centre is about 34 to 35 cm, and pivot to ball top (string only) is about 30.5 to 31.5 cm.
  The current 35.0 is within about 3% under the centre convention and about 12% under the top convention.
  No route gives a value 15% or more away from it: NO FIX.
- An unconstrained circle fit and the free pendulum fit put the pivot 18 to 25 px below the visible string top and give
  L = 0.29 to 0.31. Both are biased, because the visible string top bounds the pivot from below. Not used.

## Velocities and accelerations: not touched (no gross error by clear evidence)
Physical values, from smooth model / pendulum fit:
- v(0.3) is 1.08 to 1.17 m/s; the 1-frame forward difference is 1.16 to 1.22.
- v(0.6) is 0.53 to 0.87 instantaneous. The turning point is at t of about 0.69 to 0.73, so this value is very
  sensitive to timing. The 1-frame forward difference is about 0.71 to 0.73.
- |a(0.3)| is 4.5 to 5.8 and |a(0.6)| is 5.5 to 6.5 m/s^2. At a(0.6) the ball is near the turning point, where
  g*sin(theta0) dominates.

Label hypothesis using only the stated 0.3 s depth grid (chords with the stated ranges, hyp.py):
- v(0.3) = 1.28, v(0.6) = 0.39, a(0.3) = 5.47, a(0.6) = 3.07.

Current answers:
| row | o | s | X |
| --- | --- | --- | --- |
| v(0.3) | 1.51 | 1.24 | 1.48 |
| v(0.6) | 0.43 | 0.69 | 0.39 |
| a(0.3) | 4.89 | 4.89 | 5.02 |
| a(0.6) | 2.83 | 2.82 | 2.90 |

Every current value sits within the spread of plausible label conventions:
- 0.3 s chord on the stated grid.
- 1-frame forward difference.
- Instantaneous value with the label-noise inflation.

The s-render v(0.6) = 0.69 is the labnoise x1.6 factor (line-of-sight motion) applied to 0.432. It matches the
1-frame forward difference (0.71 to 0.73); o and X (0.43 and 0.39) match the 0.3 s chord (0.39). The renders disagree
because the label convention is unknown, not because of a wrong object, time, axis or segment. I cannot tell which is
right without labels.

a(0.6), at about 2.85, is about 2x below the physical instantaneous value of about 6. It does match the 0.3 s
chord second difference (3.07). Whether the label is instantaneous or grid-based is unknown, and the motion rows are
leaderboard-tuned, so this is not clear evidence: no change.
Fixing the s/o/X disagreement would also need a decision on the label convention. That is beyond this audit's
evidence bar.

## Result: 18 rows checked, 0 fixes
