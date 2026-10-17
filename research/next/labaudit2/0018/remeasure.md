# 0018 independent re-measure: qid 2335 (captured_0018x, "width of the box", cm)

Second measurer, done from scratch (did not read labaudit/0018 or labaudit2/0018 notes). Scripts and crops are in
`remeasure2335/` (track_fall.py, fit_fall.py, simfit.py, fit_edges.py, drag_fit.py, horizon.py, width_px.py, PNG crops).
0018, 0018s and 0018x are pixel-aligned renders of the same capture; the 0018x SAM mask was used for tracking and the
original render for edges.

## Result
**Best value: 7.5 cm** (likely range 7.3 to 7.9). Physical width is about the same, 7.4 to 7.5 cm. Confidence: medium-low.

## Pixel size of the box (held, video frames 0-28; it is static)
- The box is held upright by the near (right) hand at the top. Its printed front face is about 20.3 px wide
  (median over frames 2-20 from a half-level edge profile; 20.7 px by hand in frame 0) and 51.9 px tall (sd 0.2).
  Pixel L/W is about 2.55.
- A dark 1-2 px band under the face is the bottom face, seen from below. There is at most a 1 px side strip, so the face
  is turned towards the camera, giving the off-axis factor cos(12.7 deg) = 0.976 (1.0 if the face were fronto-parallel).
- The box covers the far (left) forearm that holds the soccer ball, so it is in front of that arm.

## Depth of the box (the hard part). Every route uses f = 711 and cx,cy = 640,360.
1. **Floor contact after the drop.** The box lands upright at video frame 39, with its lowest mask pixel at v of about
   603-605. It then bounces, tips over and lies with its near bottom edge at v of about 597-606. The soccer ball's floor
   contact (from bounce interpolation) is v of about 579.5 at ball-centre Z = 2.84 (range 2.80 + R, with R = 0.087 from a
   43.5 px diameter). The ball's pixel size stays constant during the fall, so its depth does not change.
   The horizon is v of about 332.5 at these columns, from the vanishing points of the room baseboards and panel tops plus
   orthogonality, so k = Z(v - v_h) is about 701. The two people's shoe soles against their stated ranges give k between
   667 and 737.
   This puts the box front at landing at **Z of about 2.59** (2.47-2.72 over the k range).
2. **Vertical fall.** The box's u stays at 480-487 from hold to landing, and its pixel size at rest is about the same as
   held (length 50-54.5 px against 51.9). So the box did not move much in depth: Z_hold is about Z_land.
   The floor back-projection of the resting box's bottom edge gives a length of 17.8-19.6 cm, which means a hold
   Z of 2.43-2.67.
3. **Gravity (prior g = 9.8)**, on the 25 fps capture clock with the dropped frame between video frames 35 and 36
   (double step seen for both box and ball).
   - Validation: the ball's SAM-mask centroid gives Z = 2.76-2.84 against the expected 2.84, which confirms the timing
     and f.
   - Box mid of top and bottom edges, fitted from capture frame 29: Z = 2.80 with no drag. Fitting only the late,
     fast frames gives 3.1, and the deceleration with speed looks like drag; an empty cardboard box falling end-first
     has an estimated 15-25% drag at 3-4 m/s. With a quadratic drag term (terminal speed 7-13 m/s), Z = 2.45-2.72 at
     equal rms. Gravity therefore only bounds the box centre at 2.45-2.8.
4. Being in front of the ball arm (forearm near Z 2.86-2.9) means the front face is at Z of 2.8 or less.

The routes combine to a front-face depth at hold of about **Z = 2.62 (2.56-2.76)**.

## Width
W = 20.3 px x Z x c / 711:
- Z 2.62, c 0.976-1.0 gives 7.30-7.48 cm.
- Z 2.76 gives 7.7-7.9 cm.

Label style (two clicked edge points back-projected with ToF depth on the face) is about the same as the physical
width. Click jitter of 1-2 px on a span of about 20 px adds about 5-10% noise to the label.

**Answer 7.5 cm.** The current submission's 7.85 sits at the top of my range, about 4.5% above my central value.
Recommendation: about 7.5-7.6. 7.6 would be a hedge that stays within 5% of both 7.3 and 7.95.
