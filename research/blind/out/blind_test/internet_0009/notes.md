# internet_0009 - overhead drone view of a tennis court (2160x3840, 60 fps, 111 frames)

## Setup
- Camera static (phase correlation drift < 0.6 px over the clip).
- Near top-down view. Singles sidelines (half-res fits): x = 221.5 -> 205.5 (left) and 892 -> 890.5 (right) over y = 520..1880.
  So the singles width = 1341 px at full-res y=1040, rising to 1370 px at y=3760 (slight tilt, ~2 % scale change).
  Checks: doubles/singles width ratio 1.333 (expected 1.333); baseline to service line 892 px over 5.485 m = 162.6 px/m, which matches the width scale (163.3 px/m).
- Scale used: 8.23 m / ~1345 px = 6.12 mm/px (1342-1357 px is the range over the relevant regions).
- Net: the white top cord is at y~2867 and the net base at ~2817 (the cord is pushed away from the nadir). Camera height is about 15.5-16.5 m and f is about 2600 px.
  Heads (1.7 m) therefore project ~11-12 % further from the nadir than the feet do.

## Q2047 distance between the players at t=0
- Left player (crouched, static): body centre (664,1512), head (661,1520), feet (674,1537).
- Right player: body centre (1478,970), head (1505,937), feet (1455,1021).
- Body centres: 978 px = 5.99 m. Heads: 6.29 m. Feet (true ground distance): 5.74 m.
- Answer 6.0 m (body-centre convention). Medium confidence: the error is +-5 % depending on which point an annotator clicked.

## Q2048 average ball velocity across the net
- The ball is hit by the right player at about frame 38 at (1312,1258) and tracked by background differencing in frames 44-91. It crosses the net at about frame 70 and leaves the frame at frame 92.
- Image speed over the whole flight (frames 39->91) is 50.2 px/frame = 3011 px/s, giving 18.4 m/s. Speed near the net (frames 62-74) is about 52.5 px/frame, giving 19.2 m/s.
  The image speed rises from 51 to 54 px/frame and then falls to 43 (height and perspective effects plus drag).
- Answer 18.5 m/s. Medium-high confidence for a 2D annotation; the real horizontal speed is ~5 % lower because the ball is about 1 m above the ground.

## Q2049 total displacement of the right player
- Body centre goes from (1478,970) at f0 to (1450,1447) at f110. That is 478 px = 2.92 m. Head: 3.06 m. Feet: 2.67 m.
  An automatic shadow-rejected mask centroid gives (1477,964) -> (1441,1445), which is 2.95 m.
- Answer 2.92 m. Medium confidence.
