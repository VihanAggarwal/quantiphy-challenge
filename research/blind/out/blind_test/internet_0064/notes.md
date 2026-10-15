# internet_0064 notes
Static camera, 1920x1080, 30 fps. Person throws a basketball that bounces once and goes off to the right; then the person walks right.
Scale: the ball is tracked with background difference plus a red mask (track2.py -> ball2.txt). Parabola fits on both arcs (frames 81-113 and 116-144) give g = 3531 px/s^2 (the arcs agree within 0.3%), so 0.002775 m/px.
Check: ball diameter of about 88 px gives 24.4 cm, which matches a real basketball.
- 3213 height: about 627 px from cap top to shoe bottom (frames 0 and 150), so 1.74 m. Medium confidence.
- 3214 / 3215 ball speed: parabola-fit backward difference gives 2.75 / 5.18; raw frame differences give 2.84 / 5.04. Answers 2.8 / 5.1.
- 3217: the floor contact comes from where the two arcs meet (bounce centre y about 1015, plus a 44 px radius; the visible ball bottom at the bounce is about 1047). Ball bottom at 3.5 s is y 492, giving 1.57 m. Medium confidence.
- 3218: from the fit, (3.5 s to 3.7 s) gives 1.07 m.
- 3219 / 3216 person: hip x positions read by eye (165 at frame 120, 250 at 132, 455 at 150) and head template track (head.py). Displacement is about 290 px, so 0.82 m. Speed at 4.4 s is about 11 px/frame, so 0.93 m/s. Low to medium confidence.
- 3220: 24.4 cm.
