# simulation_0209 family: independent re-measurement of qids 1587 and 1560

Measured from scratch. I did not read any other file in this folder. Scripts and crops are in `m2_q1587_q1560/`.

## Shared setup
- The four 3D clips (0202, 0205, 0206, 0209) use the same fixed camera. The fitted letter edges agree within 0.2 px
  across all four clips. The 2D clips 0203, 0204, 0207 and 0208 show the same scenes from a frontal camera that is
  aligned with the desk. The pairs are 0202/0203, 0205/0204, 0206/0207 and 0209/0208.
- 3D camera (`vp.py`, `cam.py`):
  - Vanishing points come from LSD segments: the desk short axis and the verticals give f = 2652 px; the long-axis
    vanishing point is poorly constrained. The vertical vanishing point gives pitch 13.38 deg. Roll is 0.
  - Glass-fall estimates by the sibling agents (2648, 2668) agree. I adopted f = 2655 ± 25.
  - Desk plane: 1.252 m below the camera, from the near corner at range 3.593 m. The gun at 4.704 m gives 1.223,
    which is consistent with its origin sitting about 3 cm above the desk.
  - Desk yaw in the camera frame is 28.6 deg, from the leather-inlay edges.
- Frontal camera (`frontal2.py`): the inlay side edges are linear in v, with horizon v0 of about 515-519.
  The width ratio along a row is therefore a direct measure of world-X extent at that depth.

## qid 1587: length of the letter under the gun (0209). Answer 0.27 m (was 0.14)
- Visible corners on frame 0 (subpixel edge fits, `letter_edges.py`):
  - BL (1315.8, 624.4) and FL (1363.0, 643.1).
  - The side BL-FL lies along the desk depth: 0.144 m on the plane. This matches the previous agent's 0.144.
  - The front edge runs along the desk long axis and goes under the gun after at least 0.104 m.
- So 0.144 is the SHORT side. The long side runs along the desk length, under the gun.
- Route 1, 3D view: a cream patch at (1430-1453, 606-612), between the hammer and the frame of the gun, is the letter's
  back-right corner. Evidence:
  - Its top boundary lies on the extrapolated back-edge line, within about 1 px.
  - Its right boundary has the slope of a desk-depth line.
  - In all four clips it has the same luminance as the letter, with a bluish shade from the gun.
  - Taking BR at (1442.5, 607.2) gives |BR-BL| = 0.268-0.277 m (f = 2680-2630). The corner angle is 87-88 deg.
- Route 2, frontal clips (`frontal_letter.py`):
  - The letter is fully visible: it extends past the muzzle on the left and past the grip on the right.
  - Letter X-extent divided by inlay X-extent on the same image row gives 0.1267 ± 0.0002. This holds for the back,
    middle and front rows and for all four 2D clips.
  - The inlay length from the 3D view is 2.08-2.14 m, which gives a letter length of 0.264-0.272 m.
- The frontal view also gives the depth side: 0.136-0.144 m, consistent with route 1.
- The letter is aligned with the desk within about 2 deg, so world-AABB X is about 0.27 as well. Length is 0.27 under
  either reading of length: the long side, or the side along the table length.
- Confidence: medium-high. The same letter appears in 0206 (qid 1583, current answer 0.24) and in 0203, 0204, 0207
  and 0208. It should be about 0.27 in all of them.

## qid 1560: width of the typewriter (0202). Answer 0.41 m (world AABB, desk depth axis)
- In 0202 the typewriter is yawed relative to the desk. The 0205 typewriter is aligned with the desk, so the two clips
  are not the same footage.
- Yaw:
  - Base-flange front edge, FL (1006.3, 758.1) to FR (1158.1, 703.6) on the plane: 0.371 m, yaw +21.1 deg
    relative to the desk inlay.
  - Left flange side: about +18 deg.
  - Frontal twin 0203: front edge 20.5 deg and side 17.3 deg, front 0.38 m.
  - Adopted psi = 19.5 ± 1.5 deg.
- Local footprint:
  - Front (local length): 0.37 m. Measured as 0.366 in 0205, 0.371 in 0202, 0.361 in 0209 at rest and 0.38 in 0203.
  - Depth (local width): 0.305 m. Measured as 0.302 in 0205 (3D), 0.297 in 0204 (frontal), 0.312 in 0209 at rest and
    about 0.326 in 0203, where the BL pick is uncertain.
  - Upper parts (carriage knobs, paper table) stay inside the base footprint. Evidence: the side profile in 0209
    frame 9 and the knob X in 0204.
- World AABB along the desk depth axis = l sin(psi) + w cos(psi) = 0.40-0.425, best 0.413. Flange corner rounding
  takes off about 0.005. World AABB X is about 0.455.
- If the labels instead use the local Blender dimensions, the width would be about 0.305.
- Confidence: medium. The geometry is good to about 3%; the main risk is the label convention.
