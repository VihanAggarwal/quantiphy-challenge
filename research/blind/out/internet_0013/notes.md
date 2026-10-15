# internet_0013 (top-down drone view of a roundabout, 1920x1080, 30 fps, 279 frames)

## Camera
Near-static nadir camera: LK feature tracking vs frame 0 gives <=2 px drift, 0.13 deg rotation, scale 1.001 over 9 s.
All tracking done in frame-0-stabilised coordinates (per-frame affine, work/affines.npy) with a median background (work/bg.png).

## Scale (prior: pedestrian walking speed = 1.1 m/s)
Background-subtraction blob tracks on the left sidewalk:
- single pedestrian B: 211.6 px in 9.0 s -> 23.5 px/s (path-length 23.7; linear fit 23.3)
- group A (2-3 people): f60->f270 170.5 px / 7 s -> 24.4 px/s (25.6 px/s over 0-2 s)
Adopted 24.0 px/s -> 0.04583 m/px (21.8 px/m). Range across pedestrians about +-2.5%.
Sanity: cars are 100-110 px long -> 4.6-5.0 m (plausible). The P-11 cycle-crossing squares (1.0 m period if standard) give 23.4 px/m,
which implies real walking about 1.03 m/s. That is consistent, but the prior is used as the scale.

## Measurements
- 2064 straight-through lane: the left lane with the painted straight arrow (NW->SW bypass). Curb face x~501 to lane-line centre x~598 at y=530 -> ~98 px -> 4.49 m. Medium confidence (lane identity is a guess; the right-side bypass/entry lane has variable width).
- 2065 roundabout lane: circulating lane between the truck-apron curb (r~271 px from island centre) and the lane line (r~362-366) -> ~92 px -> 4.22 m. Medium confidence.
- 2066 centre-island planter: vegetated circle 739..1184 (horizontal) and 308..755 (vertical) -> 446 px -> 20.4 m (the apron outer edge would be ~535 px = 24.5 m). Good confidence.
- 2067 white car speed at 3.0 s: car W1 (in the ring since t=0, at (1125,281) at f90): template matching with central differences 126.3 px/s. A second white car entering the ring at the bottom (855,843) moves at 131.5 px/s. Used the midpoint 128.9 px/s -> 5.91 m/s. Good confidence.
- 2068 bicycle (upper-left zebra crossing) at 3.0 s: weighted-centroid tracking on the difference image; f60->f120 141 px/2 s = 70.6 px/s; local fits 66-71 -> 3.24 m/s. Medium-good confidence.
- 2069 two black cars in ring at 1.0 s: body centres (618.5,339) and (1179,184) (from front/rear bumper midpoints) -> 581.5 px centre-to-centre -> 26.6 m. Good confidence if centre-to-centre is the intended definition.
