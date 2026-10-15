# internet_0043 notes
Static-ish camera (drift <0.2 px/frame, phase correlation). White ping-pong ball rolls right->left in front of objects.
Ball track (HSV white mask, windowed): ~44.8 px/frame at t=1.0s -> 1342 px/s; ball diameter 79 px (vertical, no blur).
Prior 33.38 cm/s -> 0.0249 cm/px at ball depth -> ball 1.96 cm, wine bottle ~15 cm, kettle ~8.4 cm: implausible by EXACTLY ~2x
(ping-pong ball 4.0 cm, 750 ml wine bottle ~30 cm, 500 ml bottle ~22 cm all consistent with 2x). Suspect a fps-factor (60 vs 30)
in the velocity label; physical sizes likely tape-measured. DECISION: use 2x prior scale (0.0503 cm/px at ball depth).
If GT follows the prior literally, divide all answers by 2.
Perspective: horizon est. y~400 (cylinder top ellipse ~7 deg); objects' bases y~752-770 vs ball contact 828 -> factor 1.16-1.20.
Pixel extents: kettle 287, cylinder 195, green bottle 516, plastic bottle 391, bowl(plate) 168, kettle-bowl centres 1020, cylinder-bottle centres 410.
Distances taken centre-to-centre (horizontal). Confidence: sizes medium (hinges on 2x decision), distances low-medium (definition).
