# simulation_0248 notes
Scene: static camera, gray studio. Red horse (left, trailing, feet y~627.3 -> slightly farther = "horse at the back"),
brown horse (right, "front", feet y~631.2), rabbit (feet y~634.7), all moving right, parallel to image plane.
Method: clean background via per-pixel temporal mode + inpainting; masks by |frame-bg| threshold; torso-band extents/centroids.
Scale: red horse torso speed 3.20 px/frame (rump, chest, centroid all agree; very uniform) = 76.8 px/s -> 0.874/76.8 = 0.01138 m/px.
Depth correction (ground-contact y, horizon assumed ~y=520, camera ~level; uncertain): brown x0.965 -> 0.01098 m/px; rabbit x0.935 -> 0.01064 m/px.
Sizes (px, manual zoomed crops at several frames + auto masks): red H 166, L 184.5; brown H 178, L 224; rabbit L 43, H 36.
Speeds at 1 s: brown torso oscillates with gait (avg 5.90 px/f, local back-diff at f24 ~6.5); used 6.2 px/f -> 1.63 m/s.
Rabbit hops, avg 6.27 px/f, back-diff at f24 ~6.3 -> 1.61 m/s.
Confidence: red sizes medium-high; brown sizes medium (depth corr.); speeds medium (gait oscillation, origin convention); rabbit sizes medium-low (pose).
