# Lab audit, family 0047 (captured_0047 / 0047s / 0047x): 9 rows, 3 questions x 3 renders

Scene: the same gray padded room as 0052/0061. A person squats at the far wall and rolls a gray yoga ball toward the camera.
The ball passes left of centre and leaves the frame at the bottom after about n42. There is **no soccer ball** in the clip.
The depth line "t=1.5s, distance_soccer_ball_camera = 1.4972m" can only be the yoga ball at 1.5 s, because the displacement
question needs it. All three renders share one SAM mask: x is a green screen, o has a blurred background, s has a blue one.

## Method (scripts/)
- `extract.py`: frames, contact sheets (`sheet_*.png`).
- `track.py` + `fit_all.py`: per-frame sphere-silhouette fit on the x render.
  - Boundary pixels next to green are selected with a robust circle band.
  - An exact pinhole cone (centre direction c, half-angle alpha) is fitted with f = 711 and the principal point at the
    image centre. This handles the off-axis ellipse stretch.
  - Fits are overlaid on the o render in `fit_overlay_o.png`; they are good for n18-42 with 1-3 px rms.
- `blobfit.py`: the same fit for any blob; used on 0052x / 0061x (frames in `other/`).
- `traj.py`, `emulate.py`: 3D track in units of R, and label emulation with the stated depths.
- Frame drop: the step n35->36 is about 1.5x its neighbours (2.31 deg vs 1.43/1.64 deg), so the 25->24 fps capture clock
  applies. n24 = 1.00 s, n35 = 1.44 s, n36 = 1.52 s.

## Model check with a known size
In 0052x the basketball (23.2 cm, stated in 0035) sits at rest, with a stated range of 1.9365 m and sin(alpha) = 0.0561.
- Range-to-front-surface model, R = r*s/(1-s): **23.0 cm**.
- Z-depth model: 25.6 cm.
- Range-to-centre model: 21.7 cm.

So f = 711 and "range at the click on the front surface" are confirmed for this room and camera.

## Yoga ball diameter (2774/2777/2780; current 52.2 / 54.9 / 55.3)
| route | D (cm) |
|---|---|
| 0047 n24 (1.0 s, 2.4985 m), sin = 0.0992 (n23 / n25: 53.2 / 56.8) | **55.0** |
| 0052 same ball, n24 (1.0 s, 2.612 m), sin = 0.1001 (n22 / n23: 54.8 / 56.7) | 58.1 |
| 0061 same ball, n14 (0.6 s, 2.133 m), sin = 0.1102 (n13 / n15: 55.3 / 50.8) | 52.9 |
| speed prior 2.1464 vs the 3D size-track speed at 1.0 s (quadratic fit n21-42) | 57.6 (about 55 after removing label-noise inflation) |
| floor plane: ball-centre plane 2.96 R below the camera (very stable); shoe floor point at about 3.7-3.83 m | 56.5-58.5 |
| 0047 1.5 s anchor (1.4972 m at n36) | 49.0 (inconsistent, see below) |

All routes give 53-58 cm, so the ball looks like a nominal 55 cm ball. The current answers are within 6%. **No fix.**

## The 1.5 s anchor is inconsistent with the ball's size
- From n24 to n36 the angular size grows by 1.417x. The stated ranges with R = 0.2765 need 1.56x.
- The size track puts the front surface at 1.68-1.70 m at 1.5 s; the stated value is 1.4972 m.
- At 1.0 s the size track gives 2.48-2.49 m against the stated 2.4985 m, which agrees.

So the stated 1.5 s range is about 0.19 m short, maybe from a bad ToF reading at the image corner. It is still the value the
labels were built from.

## Displacement 1.0 -> 1.5 s (2775/2778/2781; current 1.0898)
- Label emulation (stated ranges along the click rays, click at n35 or n36, centre or visible centre): 1.06-1.10.
- Z-model: 1.01.
- Physical centre displacement from the size track: 0.94-0.96. This is lower because the stated 1.5 s range is short.

The current value matches the emulation of the stated anchors. **No fix.**

## Yoga ball to person at 1.5 s (2776/2779/2782; current 2.312 / 2.315 / 2.312)
- Label emulation, range model: 2.45-2.57, with the person click on the head, torso, centroid or hips (about (585,420-470)).
- Z-model: 2.35-2.41.
- Physical centre to centre (ball centre from size, person surface +0-0.1 m): 2.15-2.25.

The current value is 1% below the radial lower bound |3.83 - 1.4972| = 2.333. A label built from the stated ranges cannot be
below that, so the current value is slightly low. It is still only 6-11% below the emulation and inside the spread of the
routes, so the 15% bar is not met. **No fix.** It would be a small +EV nudge to about 2.45, not a correction.

## Result
9 rows checked. No fix.
