# simulation_0053 — notes

Scene: nadir (straight-down) perspective camera over a street, 2048x2048, 30 fps, 91 frames.
Orange car (decelerating) and dark-green classic roadster drive down the image (+y); a person walks up (-y)
at bottom-left; two black street lamps on the left sidewalk (bases at ~(497,1065) and ~(497,1908)).
Lane lines are vertical and parallel (x=667/1102/1546 at every row) -> optical axis vertical; lamp poles and the
person project radially from the image centre -> pinhole camera, principal point ~ image centre.

## Scale (prior: orange car a = -2.86 m/s^2)
Template-tracked (NCC, sub-pixel) 5 orange-car features over frames ~22-90; each fits a pure quadratic
(cubic term ~0, rms 0.1-0.9 px): a_px = -312.0 (headlights/hood), -313.6 (cowl), -314.3 (rear deck),
-316.6 (roof logo / rear window) px/s^2 (using common a/v = -0.4767 1/s). Silhouette-mid: -316.
Different rates = different feature heights (y_img = f*Y/(D-h)). Camera height D estimated 25-45 m
(car feature rate ratios with typical car heights -> ~35-42; person head/feet lateral parallax -> ~25-34;
lamp apex/base radial ratio 1.188). Adopted D = 33 m, f ~ 3515 px (HFOV ~32 deg); s(h) = (33-h)/3515 m/px
(s(0)=0.00939, s(0.8)=0.00916, s(1.2)=0.00905). Answers vary <1% for D in 25-45.
Motion blur is negligible (chrome bar edges 4-6 px wide at 43 px/frame).

## Answers
- Q19 green car speed @2.0 s: constant speed (quad acc ~0). Windshield bar 1311.0 px/s (h~1.2), rear bumper
  1283.3 px/s (h~0.5), whole-car template 1292 -> 11.85-11.86 m/s. Answer 11.86. Confidence high (scale-limited).
- Q20 orange car length: silhouette bumper-to-bumper at centred frames (f48-52) 548.5 +-2 px, ends at h~0.6-0.9
  -> 5.03 m. Confidence medium-high.
- Q21 green car length: bg-difference / chrome extents at centred frames f62-63: 561-562 px (rear overriders to
  front bumper corners), h~0.5-0.6 -> 5.18 m. Confidence medium-high.
- Q22 lamp distance: base-circle centres 842.5 px apart (same x); base at ~0-0.5 m height -> 7.85 m
  (7.80-7.90 depending on D / base height). Confidence medium-high.
- Q23 person walking speed @2.0 s: in-place walk animation (feet slide back), root translates slowly and
  accelerates slightly. Jacket hem (hip line, ~1.0 m) tracked f30-90, fit trend + step oscillation (step ~15 frames):
  v(f60) = 1.70-1.74 px/frame (stride means 1.6 px/f for t=1-2 s, 1.95 px/f for t=2-3 s) -> 51.6 px/s * s(1.0)=0.0091
  -> 0.47 m/s. Confidence medium (pelvis phase oscillation unknown).
