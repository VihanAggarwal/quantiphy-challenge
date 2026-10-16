# Lab audit, family 0054 (captured_0054a/as/ax, captured_0054b/bs/bx): 71 rows

One event filmed by two cameras. Camera a is frontal and about level (vertical-VP pitch about 1 deg). Camera b is high and
looks down about 30 deg (VP from the wall seams: pitch 29.9, roll -6.5). Per the brief, all six renders share one label.
Props: the "orange ball" is a Wilson basketball (23.2 cm, stated in 0035). There is a soccer ball, a green tennis ball,
and a pale pink/white ball. The **white ball and the pink ball are the same object**: a/ax ask "pink", the others ask
"white" (there are only two juggled balls, see a_smallballs.png).

## Timing (important for the motion rows)
The video runs at 24 fps but was made from a 25 fps capture by dropping one frame in 25. Every track jumps by double steps
at n 11->12 and n 35->36, in both cameras (orange ball ax 15.9/33.0/17.9 px; green ball a y-steps 48 -> 131 -> 41).
Capture time is tc(n) = n/25 (n<=11), (n+1)/25 (12..35), (n+2)/25 (n>=36). So n24 = 1.00 s and n36 = 1.52 s.

## Small balls: 3D ballistic fits, scaled by g only (scripts/ballistic_a.py, ballistic_b.py, compare_ab.py)
Each fit uses free flight with g = 9.8 m/s^2 along the camera's gravity direction (from the vertical VP) and tc(n) timing.
No depth_info is used. Each fit's range at 1.0 s is then a check against the stated depth:
| | range at 1.0 s (fit / stated) | apex | horizontal speed | speed at 1.50 s | speed at 1.52 s |
|---|---|---|---|---|---|
| green, cam a (n24-35) | 2.94-3.08 / 3.039 | 1.07 s | 2.13-2.20 | 4.72-4.83 | 4.90-5.00 |
| green, cam b (n25-35) | 1.34-1.41 / 1.331 | 1.08 s | 2.08 | 4.55-4.61 | 4.78 |
| white, cam a (n29-35) | 2.9-3.5 / 3.0735 | 1.10 s | 2.33-2.46 | 4.38-5.09 (4.6) | 4.76-4.80 |
| white, cam b | 1.23-1.38 / 1.235 | 1.10 s | 1.83-1.99 | 4.28-4.37 | 4.55 |
The two cameras agree on the apex time, the horizontal speed and the speed at 1.5 s. The gravity scale reproduces the stated
ToF ranges in both cameras (within 1-5%).

Bounce timing: the green ball hits the floor between 1.52 and 1.56 s (at n37 it sits 27 px above the free-flight
prediction). The white ball hits between n37 and n38.
- Green at 1.5 s: about 4.7 m/s instantaneous. Forward differences give 4.72 (1.48->1.52) or 5.07 (1.52->1.56, no bounce),
  and 3.5 if the difference straddles the bounce. The current b values 1.37/1.19/1.17 and the as value 2.02 are below every
  variant.
- White at 1.5 s: about 4.5 m/s instantaneous, 4.4-5.0 for any forward difference (no bounce inside).
- Why b is wrong: at 1.5 s the ball is 2.33 m from camera b (1.33 m at 1.0 s), and 80% of its velocity runs along b's line
  of sight (v_los 3.7 of 4.6 m/s). Image speed times the 1.0 s depth gives 1.4-1.56. That is the b geometry (raw geo
  1.24/1.08/0.95 green, 1.65/1.82/1.81 white): wrong depth and wrong axis.

## Sizes
- White ball diameter: measured from the ellipse minor axis (across the blur).
  - Cam b (bx masks, n26-33): 6.8-7.4 cm with fit ranges, 6.1-6.7 cm with the stated-scaled ranges.
  - Cam a (ax, near the apex at n25-28, 15.5-17 px at about 2.95 m): 6.3-7.0 cm.
  - White/green ratio: 1.07 (a) and 1.09-1.13 (b), so 7.2-7.5 cm if green is the 6.7 cm tennis ball. The same method reads
    the green ball at 6.0-6.6 cm.
  - Central value about 6.7 cm.
  - b's 5.39 is the outlier, because at 1.0 s the white ball is fused with the green ball in b (bx_gw.png, n24) and b's
    geometry read about 31 px.
  - as 7.72 equals its blur-inclusive extent (n24 ellipse 14.6 x 20.6 px) and sits inside the tennis-ratio bracket, so it is
    left as it is.
- Soccer ball diameter:
  - Route S1: ratio to the basketball at rest in a n0 (65 vs 70.5 px, both on the floor). Gives 19.8-20.0 cm for any
    camera height or pitch.
  - Route S2: b n48 (2.0 s, stated 3.254 m, 44-47 px). Gives 19.4-21.4 cm.
  - Current 18.36/19.0 is within 5-9% (and labels read stated sizes about 1.056x low). No fix.
- Orange ball diameter 23.2: this is the basketball, stated in 0035. No fix.

## Distances / displacements
- Orange displacement 0.5->1.0 s:
  - a-route (label emulation with the stated 2.3557 / 1.81 along the n12/n24 centre rays): 0.85-0.88.
  - b-route (b's own sizes, or b's 2.24 plus the size ratio): 0.94-0.95.
  - b's depth_info "1.81 at 1.0 s" is copied from a. b sees the ball recede (75 -> 61 px; about 2.7 m at 1.0 s).
  - Current a 0.865-0.870 and b 0.80: the routes disagree by 9% and no current value is 15% off. No fix.
- Soccer displacement 1.0->1.4 s:
  - The b size route depends on the occluded rest size (62-68 px) and gives 0.40-0.65.
  - labstatic's a-floor route gives 0.27-0.36.
  - Current 0.37-0.45 lies within that spread. No fix.
- Orange-soccer distance at 1.0 s:
  - b (sizes): 1.50-1.58.
  - a: 1.30-1.71, strongly dependent on the soccer range. 1.43-1.48 with the soccer at 20 cm by size, 1.30-1.40 if ToF reads
    the soccer about 7% short like the orange ball.
  - Current a 1.46-1.56 and b 1.33: no route pair agrees within 8% at 15% from current. No fix (as in labstatic D).
- Green-white distance at 1.0 s: a stated ranges at the n24 centres give 0.155, b stated at the fit-projected centres gives
  0.132. Current 0.138-0.172 is fine.

## Motion rows left alone
- Soccer velocity at 0.5 s: the ball rests under the person's hand (ax centre moves less than 1 px over n10-14), so the
  physical speed is about 0. The label is click/ToF noise, so the 0.02-0.15 spread cannot be judged. Untouched.
- Green and white at 1.0 s: about 2.2-2.3 (green), about 2.2-2.6 (white). Current 1.70-2.29 is not grossly wrong.
- Green 1.5 s, a 4.30 and ax 5.42: within the 1.5x bound of 4.7.
- Pink/white 1.5 s, a 5.92 and ax 6.70: 1.3x and 1.46x of 4.6. Not over 1.5x, and they sit on the noise-correction side.
- White 1.5 s, as 3.19: 1.44x below 4.6. Just under the 1.5x rule, so it is left as it is (borderline; it is +EV to set it
  to 4.6).

## Fixes (two camera routes agreeing within 8%; current value at least 15% off and more than 1.5x off for speeds)
| qid | render | row | current | new |
|---|---|---|---|---|
| 2851 | as | green velocity 1.5 s | 2.02 | 4.7 |
| 2874 / 2886 / 2898 | b / bs / bx | green velocity 1.5 s | 1.37 / 1.19 / 1.17 | 4.7 |
| 2875 / 2887 / 2899 | b / bs / bx | white velocity 1.5 s | 1.75 / 1.64 / 1.64 | 4.6 |
| 2870 | b | white ball diameter | 5.39 | 6.7 |

The speeds are physical, with no label-noise factor. In this family the stated prior (orange at 0.5 s = 2.21) is about 1.1-1.15x
the measured physical speed (1.8-2.1 m/s in 3D from multi-frame size-range differences in both cameras), so applying the pipeline's small-ball factor of about 1.1 would also be
defensible: green about 5.1, white about 5.0. For green there is the opposite risk of a bounce-straddling label (about 3.5).
