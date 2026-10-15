# internet_0044 notes
Scale from gravity: tracked ping-pong ball (bg-median subtraction + white mask, track.py -> track.txt), parabola fits on 6 clean
flight segments give g = 18.2-20.5 px/frame^2 (mean 19.5, full-res 1920px). 9.8/900 m/f^2 / 19.5 -> 0.05584 cm/px.
Ball bounces with bottom at y~805-810, same as object bases (~810-815) -> same depth as objects. Camera drift ~0.1 px/frame (cam.py), negligible.
Pixel extents (frame 15, full res): ball ~70 px (vertical near apex), kettle 286, cylinder 197, green bottle 513, plastic bottle 387,
bowl/plate 164. Distances centre-to-centre: bowl cx 309 - kettle bbox cx 1325 = 1016 px; bottle cx 621 - cylinder cx 1032 = 411 px
(gap alternatives: 36.3 cm and 16.4 cm).
Velocity: backward difference of parabola-fit track; f45: 52.9 px/f -> 0.886 m/s; f75: 36.5 px/f -> 0.611 m/s.
Confidence: sizes medium-high (scale +-5%); distances medium (centre vs gap convention); velocities medium.
