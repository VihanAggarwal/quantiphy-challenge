# internet_0012 - top-down drone view of a 3+3 lane bridge (2160x3840, 108 frames, fps 60)

## Scale
- Lane lines fitted on a vehicle-free background composite (frame 0 with vehicle boxes filled from frame 107).
- Lane widths (centre-to-centre of markings, px): left carriageway 98.5 / 96.6 / 100.2, right 99.1 / 96.4 / 99.9;
  3-lane totals 295.35 px at both carriageways, constant along y (no perspective, nadir view, road tilted 0.4 deg).
- Used 98.2 px per 3.66 m lane -> s = 0.03727 m/px.

## Camera
- Near-static: LK features + RANSAC similarity on the bridge give cumulative drift ~8.6 px down, 0.1% scale,
  0.06 deg rotation over the clip; all frames warped to frame-0 coordinates before measurement.
- Video has near-duplicate frames (frame-rate conversion); speeds use linear fits over all 108 frames with t = frame/60.

## Vehicles (background subtraction with a 5x5 min/max-tolerant background, connected components per lane corridor)
- truck: right carriageway, rightmost lane, moving up. Length (mask) 470-483 px (median 475), half-max edges median 466.
  Apparent length shrinks as it nears the image centre (vehicle height parallax, h/H ~ 0.02-0.03). Used ~473 px -> 17.6 m.
  Speed: centre-track slope 373 px/s -> 13.9 m/s.
- grey car (dark grey, right carriageway middle lane, moving up): length 130-137 px (mask median 135, visual 127-134) -> ~132 px -> 4.92 m.
  Speed 548 px/s -> 20.4 m/s.
- car on leftmost lane (light/white hatchback, left carriageway lane 1, straddling dash, moving down):
  length 105-111 px (median 108, visual 106-110) -> 4.0 m. Speed 308 px/s -> 11.5 m/s.
- white car on second lane from left (sedan, left carriageway lane 2, moving down): mask 124-130 (median 125), visual ~121-123
  -> 123 px -> 4.6 m. Speed 375 px/s -> 14.0 m/s.
- Front-edge, back-edge, mask-midpoint and centroid tracks agree to within 1% for every speed; endpoint displacement agrees too.

## Confidence
- Speeds: high (tracking precise to <1%); main uncertainty is lane-width pixel definition (+-2%) and time base (60 vs 59.35 fps).
- Lengths: medium-high; +-3-4% from frame-dependent parallax and edge definition, +-2% from scale.
