# simulation_0125 — notes

Scene: static, level, frontal camera on an A-frame cabin (1080x1080, 24 fps, 71 frames; frame 0 duplicates frame 1).
A person walks left->right along the recessed porch; potted monstera on the porch at left.

## Scale from the prior (speed of person = 1.22 m/s)
- Clean background = frame 70 (left half) + frame 0 (right half); person mask by background difference (overlays checked).
- Linear fit of head-x / pelvis-band-x / mask centroid vs frame (frames 1-70): 5.58 / 5.58 / 5.62 px/frame -> 134.2 px/s.
  Walking speed is constant over the clip (head x residual std 1.35 px).
- s_person = 1.22 / 134.2 = 0.00909 m/px. Cross-checks: step length/height ~0.44 (normal gait); back-wall door ~2.15 m.

## Perspective (house is closer than the person)
- Vertical edges are exactly vertical -> zero pitch, horizon = y 540. Camera centred on the house (x 537).
- Porch floor top visible 864.75..876.5 px; wood side-wall bands ~11.5 px -> porch recess depth ~3.4% of distance
  (consistent left/right/floor -> principal point at centre).
- Black frame = front faces (no lit upward face under the porch floor; the 183/891 px line is a trim line, not a depth edge).
- Person feet contact y 866.75 -> Z_front/Z_person = (866.75-540)/(876.5-540) = 0.971.  s_front = 0.00883 m/px.
- Plant stand contact ~866 -> plant scale 1.002 x person scale.

## Answers
- 281 person height: head top (highest, mid-stance) 656.3, sole 866.75 -> 210.5 px -> 1.913 m; +small standing allowance -> 1.92 m. Confidence medium-high.
- 278 plant height: top leaf ~715, stand bottom ~866 -> ~151 px x 0.00911 -> 1.38 m. Confidence medium-high.
- 280 house width: black frame outer edges 150.5..923.5 = 773 px at front plane x 0.00883 -> 6.83 m. Confidence medium
  (if the GT house object includes the deck, which runs past the right image edge, true width would be larger, >=7.8 m).
- 279 house height: apex y 27 to base at deck top y 913.5 = 886.5 px x 0.00883 -> 7.83 m; reported 7.85 (deck thickness
  ~0.12 m would add if included). Confidence medium.
