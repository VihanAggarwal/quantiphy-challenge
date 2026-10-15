# simulation_0008 - boat passing a pier in front of a stilt cabin (S3MC, 24 fps, 66 frames = 2.75 s)

## Camera / scale
- Horizon from sky-cloud reflection symmetry (flat mirror water): y_h = 532.75 px (stable 532.5-533 across patches).
- Boat: a rowboat moving right to left at almost constant depth. Bow stem tracked by template matching (rms 0.4 px).
  The waterline under the stem rises 7 px over the clip, and the pixel speed falls 7%. Both fit ONE model:
  constant world velocity with a slight move away from the camera (Z +3.6% over the clip, about 3 deg to the image plane).
  A u-only fit and the waterline fit give the same recession rate.
- Boat-height prior: stem top at y=619.7, stem waterline at y=744.25 (mirror line). The stem top is the bbox top and the keel
  sits at the water line (zero draft), so the stem is 0.5889 of the camera height above water -> h_w = 1.274 m.
  Zero draft is supported by the ranges: a fit using only the ranges gives h_w = 1.305 (it would need stem > 0.75 m, which is impossible).
- Focal length: ranges r(0)=7.452, r(1)=6.655 to the boat bbox centre (bow-stern midpoint), with h_w fixed, give f = 963-980 px.
  The pier-centre range 11.579 (bbox centre between front face Z_f and back edge) gives f ~ 955-960. Used f = 965 px (FOV ~58 deg).
## Measurements
- Pier front: beam top y=629.5, beam/post water mirror line y=675.6, front beam x 458.5-637.5 (179 px).
  Z_f = f*h_w/142.85 = 8.60 m. The deck is flat at the beam-top height: the width/(y-y_h) ratio is constant, and the back edge is at y=589.5.
- Width = 179*h_w/142.85 = 1.60 m (does not depend on f). Deck height = 46.1*h_w/142.85 = 0.41 m (does not depend on f).
- Length: image back edge gives 6.06 m. The centre-range route (11.579, origin at bbox centre) gives 5.74-5.85 m. Answer 5.9 m.
- Boat speed: Vx = h_w*a1*24 = -1.490 m/s (does not depend on f), Vz = 0.077 m/s -> |v| = 1.49 m/s.
  The range-only solution gives 1.53 m/s. Answer 1.50 m/s (constant velocity, so the 1-2 s average equals this).
- t=3 s (frame 72, extrapolated past the clip end): boat centre at X~0.2 m, directly in front of the pier (X -0.73..0.87).
  Far hull side (half-beam about 0.64 m, from gunwale and mirror geometry) at Z ~6.53 m. Gap to the pier front face = 8.60-6.53 ~ 2.05 m.
- Stairs (range 17.623): open treads between the porch posts at x 490-585 and newel posts at 500-600. 95-100 px at Z 17.1-17.6 m -> 1.73-1.82 m. Answer 1.78 m.
- Cabin floor: porch floor edge y~522.5 (0.19 m above the camera at Z~18.1), ground at the stair base y~586 (0.95 m below the camera at Z~17.1)
  -> 1.14-1.17 m. Answer 1.15 m.
## Confidence
1037 width: medium-high. 1041 deck height: medium-high (depends on zero draft and the bbox-top definition).
1043 speed: medium-high. 1038 length: medium (back edge partly hidden by grass, about ±4%).
1039 min distance: medium-low (depends on how "min distance" is defined; origin-to-front-centre would be about 2.7 m).
1040 stairs width: medium-low (unclear which parts belong to the stairs object). 1042 floor height: medium-low.
