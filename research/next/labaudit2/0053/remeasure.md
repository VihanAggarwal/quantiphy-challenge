# 0053 independent remeasure (qids 2817, 2825, 2830)

Scripts and scratch are in `r2/`. Camera: f=711 px, principal point (640,360). The shared depth row
(t=0.4 s) gives cup 2.516 m, book 2.082 m, ball 2.925 m and bin 2.73 m.

Scale check: the basketball is static and is 23.2 cm (stated in 0035a). Its mask in 0053x is an ellipse
of 61.1 x 66.8 px. The pinhole model at range 2.925+0.116 m predicts 60.4 x 67.2 px, so f=711 and the
stated depth agree to within 1% (r2/ball.py).

## 2817 / 2825: rim diameter of the white cup. Answer 9.15 cm (shared label for 0053, 0053s and 0053x)
- Route 1 (this clip): the outer rim width is 26.0-26.6 px. Edge widths measured with subpixel gradients
  on the 48-frame median are 26.0 (x), 26.0 (s) and 25.8-26.6 (plain); the alpha-sum mask width is 26.4-26.7.
  I modelled the 3D rim, starting from the click on the body front surface (2.516 m), stepping to the axis
  and up to the rim, with a pitch of 35-38 deg. The two corrections nearly cancel, giving z_rim ~2.51 m.
  Result: D = 26.1*2.51/711 = 9.2 cm (range 9.05-9.35). The f=711 calibrated on the ball gives the same
  (r2/cuprim.py, r2/cupedge.py).
- Route 2 (same tumbler in other clips, a physical check): white tapered tumbler with a steel rim.
  - 0038: 72 px wide at 0.874 m, giving 9.1 cm with the axis correction (8.7 cm using front-surface depth).
  - 0037/0040: 74 px wide at 0.845/0.842 m, giving 9.0 cm (8.6 cm front-surface).
  - The credit card in 0038 reads about 5% large at f=711, so the physical rim could be as small as about 8.6.
- Current answers 7.9 and 8.4 would need a rim of 22-23.5 px, which I do not see.
- Confidence: medium. The label method is unknown: clicking inside the rim edge or a ToF depth that
  bleeds to the floor behind would shift the value.

## 2830: displacement of the trashbin from 0.4 s to 1.4 s. Answer 0.97 m (label-style = physical)
- Frame mapping: the bin's mask-centroid steps double at video 11->12 (19.7 px against about 11) and at
  35->36 (13.2 px against about 6). So capture 10 = video 10 and capture 35 = video 34.
- The bin is a box lying on its side. It slides without rolling (the pose looks constant) and yaws
  about 10 deg between 0.4 s and 1.4 s.
- Route 1 (rigid planar motion): KLT tracks on the bin were run from refs 10/22/34, on the plain, s and x
  renders. Fitting planar motion (rotation about the floor normal n, translation perpendicular to n),
  with the Sampson error swept over a grid of n, gives a valley from (pitch,roll) = (30,15) through
  (37,10) to (45,1). Along the whole valley the displacement is 0.955-0.984 m and range@1.4 is 3.13-3.18 m.
- Route 2 (image vanishing points, constant click height): the wall-seam vertical vanishing point gives
  0.996 and the corridor/carpet horizon gives 0.944. The cup axis tilt (about -3 deg) also supports a
  roll of about 6-10 deg.
- Check: silhouette size (sqrt(area*cos^3)) times the predicted range stays within +-3% over all 48
  frames for valley n.
- Outlier: a floor plane fitted to the stated depths (ball, book, cup, with assumed heights) gives
  roll ~1.4 deg, range@1.4 = 3.32 and D = 1.07. That n is off the KLT valley (residual 3x worse) and gives
  an 11% size*range drift, so I reject it. The stated depths are mutually inconsistent with the image
  geometry by 10-25 cm (ball and book); I could not explain why.
- Speed check: the forward difference 10->11 is 1.03-1.04 m/s and the smoothed v(0.4) is 1.06, against
  the stated prior of 0.996 (a click-noise level difference).
- Sensitivity: one frame off in the mapping gives 0.94 or 1.00. Using the bbox centre instead of the
  centroid changes nothing.
- Confidence: medium. Most of the risk is whether the ToF world matches the image geometry
  (1.07 if the stated-depth plane is the true one).
