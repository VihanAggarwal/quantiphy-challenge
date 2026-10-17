# sim3audit group5: simulation_0195 + 0201 + 0242 + 0312

## Family check
These four clips are not one Blender scene. They are four unrelated singletons:
- 0195: Jupiter with orbiting Callisto
- 0201: droplet falling from a dropper bottle
- 0242: two horses and a rabbit in front of a house
- 0312: a red puffy star

They share no object and no motion, so a cross-clip consistency check does not apply. Each row was audited by re-measuring it on the frames, as the singleton rule asks. No row in the group has 'stated fact' provenance.

Scripts are in `scripts/`, and the frames and crops I looked at are in `frames/`.

## simulation_0201: droplet (qids 1445, 1446, 1447)
- Own track (`scripts/drop_track.py`): the droplet is found in frames 0-9 by differencing against frames 11-13, which have no droplet. Its widths go 121 px to 101 px over frames 0-6. That ratio is 1.198, against a given range ratio of 0.186/0.156 = 1.192, which supports the range convention.
- Own line-model fit (`scripts/drop_route3.py`, own LM):
  - Model: principal point at the image centre, P0 = 0.156 m along the frame-0 ray, fall direction free, s = v0 t + 0.5*9.7 t^2, |P(0.1)| = 0.186.
  - Result: f = 3658 (3708 using frames 0-7), v0 = 0.013 m/s, 1.4 px RMS.
  - Backward-difference speeds: 0.417 / 0.902 / 1.872 at t = 0.05 / 0.1 / 0.2.
  - Current answers are 0.413 / 0.898 / 1.868, all within 1%.
- A per-frame range taken from the drop width alone is too noisy to give the acceleration, because the drop wobbles after it detaches (`drop_route2.py`). That route was not used.
- Verdict: keep. The drop is released from rest at t = 0, so the answers are set by the prior (a = 9.7) and the backward-difference convention. Older submissions gave 0.49 / 0.97 / 1.94, which is the instantaneous a*t and the wrong convention.
- Residual risk: t = 0.2 s is after the drop leaves the frame (after frame 9), so that answer assumes free fall continues. The frame shows nothing the drop could hit.

## simulation_0195: Jupiter + Callisto (qids 1554, 1555, 1556)
- Own check (`scripts/callisto_check.py`) uses only three image points: the Jupiter centroid (940.4, 489.1) and my Callisto centroids at frames 0 and 90.
  - The equal-radius condition |P0 - J| = |P90 - J| holds only at f ≈ 2667. That condition does not use the speed prior.
  - Independently, the chord |P90 - P0| = 1.865 matches the speed-prior chord of 1.866 at the same f.
  - So R = 4.26 m and the orbital diameter is 8.52 (current 8.514).
- Jupiter is 282-283 px across. At 16.549 m and f = 2667 that gives 1.747-1.754 m (current 1.753).
- Callisto diameter (`scripts/callisto_size.py`):
  - edge coverage normalised by the interior median: 0.126 m (biased low by limb darkening)
  - radial half-max: 0.130 m
  - threshold-12 mask: about 0.138-0.142 m
  - Current 0.133 sits inside that 0.126-0.142 band.
- Verdict: keep all three.

## simulation_0242: horses, rabbit, house (qids 1621-1627)
- Own torso template tracks (`scripts/animals_track.py`) give pixel speeds of brown 140.2, white 268.2 and rabbit 271.6 px/s. The agent had 140.5 / 266.8 / 270.0.
- Range-rate check, independent of the agent's camera fit. Each animal walks along camera X at constant image row, so r1^2 - r0^2 = 2 X_mid V.
  - Brown horse (V = 0.874 prior): X_mid = -3.262 m.
  - Combined with the brown pixel speed (f = 160.4 * Zc_torso), the root should sit at image x ≈ 464 at frame 12. The brown horse's body centre there is at 455-498, so the geometry is consistent and f ≈ 2410.
  - Speeds with own Zc values (torso about 0.84 m nearer than the ground root because of the 40 deg tilt):
    - white: 0.874 * (268.2/140.2) * 14.04/15.03 = 1.56 (current 1.55)
    - rabbit: 1.59 (current 1.565)
- Brown horse length:
  - 325 px tail to blob front at Zc ≈ 15.1, f ≈ 2410, gives 2.03 m (current 2.09, 3% apart).
  - White and rabbit lengths scale the same way and agree within about 3%.
  - Both horse heads are covered by the face-blur blob, so the nose position is uncertain by about ±5%.
  - The two horses are different models (slender brown riding horse, stocky white horse), so equal lengths should not be forced.
- House width 8.2:
  - The brick ground floor is about 7.1 m. The jettied upper floor is wider, and the roof is out of frame.
  - No second route is possible, so I left it.
- Window width 0.74 is within about 3% of the outer-frame width of 0.75-0.76. Not worth a change.
- Verdict: keep all seven.

## simulation_0312: star (qids 1631, 1632, 1633)
- Speed:
  - The ranges 6.552 m (t=1) and 8.345 m (t=2) with the image rows give the same height below the camera (2.62 vs 2.63 m at 18.4 deg pitch), so the motion is planar.
  - The horizontal chord over t = 1-2 s is about 2.2 m at f = 1459.
  - The agent's circular-motion speed of 2.08-2.13 is consistent with this. Keep.
- Width: a regular 5-point star has W/H = 2 sin72 / (1 + cos36) = 1.0515, giving 0.210 m. Keep.
- Thickness: see the star-fit section below.
- Thickness: own silhouette fit, an independent implementation (`scripts/star_fit.py`, `scripts/star_fit2.py`, own LM in `scripts/lm.py`).
  - Model: a rounded extruded 5-point star rendered with full perspective at f = 1459 and 18.4 deg pitch, upright, with a fixed yaw. Per-frame range and centre are free. Fitted jointly on frames 0, 3, 6, 9, 12, 18, 24, 36, 48, 60 and 71 against a soft alpha mask.
  - v1 ties the 2D roundness to the 3D sphere rounding (thickness >= 2b). It gives T/H = 0.169-0.191 (cost 38.5-42.7). It is biased up: the fat 2D outline forces a large b. Fixing T/H at 0.135 in v1 costs only 40.6.
  - v2 frees the 2D in-plane rounding c from the sphere rounding b, the same model class the agent used. It fits clearly better (cost 29.1-29.2 from both yaw starts) and gives T/H = 0.125-0.1275, so thickness is 0.0250-0.0255 m. W/H comes out at 1.039-1.041, so width is 0.208 m.
  - Overlays: `frames/star_fit*_overlay.png`.
  - The per-frame ranges from the fit have the ratio Z48/Z24 = 1.275, against 1.274 from the given values.
  - Current 0.027 is about 6-8% above my 0.025, so the change is under 15%. Keep.
- Speed: own centroid + soft-height depth route, anchored to both given ranges (`scripts/star_speed.py`). The mean of per-frame speeds is 2.03-2.10 m/s across f = 1428/1459 and the range/Z conventions. End-to-end chord over time is 1.91-1.98. Current 2.08. Keep.
- Verdict: keep all three.

## Result
- Rows checked: 16.
- Proposed fixes: none. Every row I could re-measure agrees with the current answer within about 1-8%.
- The only rows I could not check with a second route are 1622 (house width 8.2, because the roof is out of frame) and the horse lengths 1621/1625 (heads hidden by the face-blur blob). There I have no evidence that the current value is wrong, so nothing was changed.
