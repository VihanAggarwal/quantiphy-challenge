# simulation_0090 (V2MX, 2D planar, 24 fps, 30 frames, 1920x1080)
Scene: bald eagle (big bird) and crow-like small bird flying right->left across plain sky; both leave frame by f19-20.
Video frames 0 and 1 are identical (first-frame hold); motion steps are uniform from f1 onward. Used video frame index = round(t*fps).

Method: median background from empty frames 20-29 (blurred), max-channel |diff| masks (th 6-15, noise max ~6),
connected components per bird; leftmost/rightmost columns (beak tip / tail tip) tracked per frame. Overlays checked.
- Small bird: left & right edges f3->f18 both move 1435 px / 15 frames = 95.67 px/frame (9-frame flap period gives 95.63). Pure horizontal.
  Scale = 11 / (95.65*24) = 0.004792 m/px.
- Eagle: left edges f2->f10 156.25 px/frame, right edges 156.375 -> 156.3 px/frame. Ratio 1.634 -> 17.97 m/s.
- Body lengths (beak tip to tail tip horizontal extent, wings never exceed it): eagle 181-182 px (very stable) -> 0.867 m;
  small bird 110-114 px (median ~112 incl. ~1 px antialias, ~111) -> 0.532 m.
- Distance at 0.3 s (frame 7): eagle bbox mid 701, small bird mid 1180 -> 479 px (vertical offset ~<10 px) = 2.295 m;
  at continuous frame 7.2: 491 px = 2.353 m. Answer 2.31 m. Separation grows 60.6 px/frame, so frame-offset risk (f8 -> 2.59 m).

Answers / confidence:
- 142 eagle speed 17.97 m/s (high)
- 143 distance 2.31 m (medium: origin location and frame indexing)
- 144 eagle length 0.867 m (medium-high)
- 145 small bird length 0.532 m (medium-high)
