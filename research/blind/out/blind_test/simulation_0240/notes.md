# simulation_0240 notes
Scene: static, level-looking camera, frontal house; brown horse (back, against wall), grey/cream horse (front), rabbit (front-most), all moving left->right parallel to image. Video has 50 frames; frame 49 loops back to frame 0 (ignored).

Tracking (template matching, colour mask, clean-bg segmentation): brown 3.15-3.25 px/frame (used 3.2 -> 76.8 px/s);
grey 5.96-6.0 px/frame (local at 1 s ~6.0); rabbit ~6.0-6.2 px/frame (local at 1 s ~6.0, used 6.05).
Scale brown: 0.874/76.8 = 0.01138 m/px.

Depth correction via ground-contact rows: brown 1046, grey 1055, rabbit 1061, house base ~1041 (hidden by grass).
Horizon ambiguous: level-camera 960 vs sky/ground boundary 987; used compromise 973.
s_grey = 0.01138*73/82 = 0.01013; s_rabbit = 0.01138*73/88 = 0.00944; s_house ~0.0118 (wall), 0.0117 (front eaves).

Pixel extents: brown 183 L x 162 H; grey 222 L x 175 H; rabbit L 41; house eaves 176..904 (728), finial 256 to base ~1041 (785);
middle window 66 W x 106 H (incl. frame).

Confidence: brown sizes high-med; house/windows medium (depth of wall vs horse ~+/-5%); grey/rabbit medium (horizon choice +/-3-5%), rabbit length low-med (blurry, in grass).
