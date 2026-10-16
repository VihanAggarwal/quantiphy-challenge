# Lab audit, family 0020 (captured_0020 / 0020s / 0020x; 49 video frames each, 24 fps container, 1280x720)

Scene: two people throw objects to each other in the lab room. The near person (left, cut by the frame edge) throws a
small white jar (a cylinder with a lid) up and over to the far person, who catches it at video frame ~28. At the same
time the far person throws the yellow toy toward the near person. The toy is a pineapple toy: a yellow body with an
olive-green crown. The near person catches it at video frame ~25. Both objects are released at about video frame 13-14,
which is t = 0.60 s on the capture clock. All three renders share one event and one set of labels. o has a blurred
background, s has a blue background, x has a green background. Pixel tracks agree across the renders to about 1 px.

Camera: f = 711 px (722 was also tried; no conclusion changes), principal point (640,360). The gravity direction comes
from the vertical vanishing point of the wall-panel seams and the vent-box edges, at about (895,1600). That gives
down = (0.18, 0.85, 0.49), so the camera pitches down about 29 deg and rolls about 12 deg. Floor model: the camera is
about 1.37 m above the floor.

Clock: the jar track jumps 93 px between video frames 11 and 12, where its other steps are about 35 px. The toy jumps
39 px against about 10. This matches the earlier lab finding of a 25 fps capture clock with one frame dropped after
video frame 11 (tau = (n + [n>=12] + [n>=36]) / 25), so video frame 14 is t = 0.60 s and video frame 19 is t = 0.80 s.
Check: fits with gravity alone and no depth anchor give a range at 0.60 s of 2.07-2.10 m for the jar (stated 1.9735)
and 2.83-2.92 m for the toy (stated 2.63). These agree to 5-11%, so the clock, f and the stated depths are consistent.

Scripts (scripts/): extract.py, montage.py, crop.py, cropc.py, detect.py/jardetect.py/track.py (2D tracks into
tracks.json), xseg.py (green-screen segmentation), lines.py/vlines.py (vertical vanishing point), people.py and floor.py
(distance between the people), ballfit.py/ballfit2.py (constant-g 3D fits, numpy LM in lm.py), perpwidth.py,
jarsize.py, toymask.py, axisprof.py (sizes).

## Rows (the same verdict applies to the o/s/x renders)
| qids | question | current o/s/x | my routes | verdict |
|---|---|---|---|---|
| 2350/2358/2366 | yellow toy height | 15.9/14.3/14.4 | In flight at t=0.60-0.68 s, with the anchored range 2.63 m and the fitted ranges 2.53 and 2.43 m, the length from body to crown tip (body axis nearly perpendicular to motion, so little blur): yellow mask s>90 gives 14.2-15.4 cm; s>70 gives 16.9-18.2 cm; the half-max saturation profile gives 16.7-17.8 cm (one outlier, 22 cm, where the hand touches). End frames in the near person's hand are occluded and their depth is unknown, so not used. | OK. My best estimate is 15-17.5 cm, within about 10% of every render's value. |
| 2351/2359/2367 | white jar height | 7.9/8.4/8.4 | Apex frames (video 21-25) with ranges from the anchored ballistic fit (2.36-2.67 m): max Feret 9.1-10.8 cm, min Feret 7.7-9.4 cm (v>190, includes halo and blur). This fits a cylinder of about 7 x 8 cm (diagonal 10.4). | OK (no route gives a >15% difference) |
| 2352/2360/2368 | white jar diameter | 6.7/7.1/7.1 | Same frames. The lid ellipse in the near person's hand at video frames 3-5 is about 34 px across: 6.9-7.9 cm if the hand is at 1.45-1.65 m (depth not stated). | OK |
| 2353/2361/2369 | distance between the people | 235.4/240.2/236.4 | (1) Back-projecting plausible torso clicks with 1.58 and 3.237 m: 233-255 cm, median 240 (centroid clicks 241.7). (2) Floor route (far torso dropped along gravity to the feet gives camera height 1.37 m; the near foot on the floor plane): feet 237-242 cm apart horizontally; torso to torso 236-246 cm. | OK |
| 2354/2362/2370 | toy velocity at 0.60 s | 274.9 | Constant-g fit plus range anchor, label-style forward difference over 0.60-0.64 s: 331-338 cm/s with the vanishing-point gravity direction; 273-317 with a free gravity direction. Earlier labfit: 315. | Not grossly off (<1.5x); motion row left alone |
| 2355/2363/2371 | jar velocity at 0.60 s | 383.0 | Same method: 342-344 cm/s (fixed gravity), 348-365 (free); instantaneous 356-382. Earlier labfit: 309. | OK / not grossly off |
| 2356/2364/2372 | toy displacement 0.60-0.80 s | 50.4 | Ballistic fit with range anchor: 59.6-61.3 cm (fixed gravity), 52.4-57.5 (free gravity); range at 0.80 s 2.13-2.25 m. The routes spread 52-61 (+4% to +22%), so the 15% / 8%-agreement bar is not met. The jar passing in front of the toy at video frame 18 is consistent with both fits. | Leave (maybe 10-20% low, not a clear error) |
| 2357/2365/2373 | jar displacement 0.60-0.80 s | 57.1 | Ballistic fit with anchor: 56.1-60.0 cm across renders and gravity options | OK |

Notes:
- The current answers differ between renders on the size rows (for example toy 15.9 against 14.3). All of them fall inside my
  measurement range, so there is no basis to pick one.
- The motion rows were checked only for gross errors (wrong object, time or segment). None was found. Both objects are
  released right at 0.60 s, the forward differences are taken in free flight, and the 0.60-0.80 s window ends before
  either catch (toy video frame 25, jar video frame 28).

Result: no fixes for family 0020.
