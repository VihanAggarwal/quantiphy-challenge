# simulation_0132: apple rolls off a kitchen island (A2MC, prior g = 9.8 m/s^2, 120 fps, 1080x1920)

## Scene
The camera is fixed and level: vertical edges are exactly vertical (x=240.5 +/- 1 px from y=400 to 1440, and the island edge at x=351 from y=1220 to 1860).
The apple starts at rest on a leaning cutting board (frames 0-~108). It rolls onto the island top, where its top edge stays constant
at y=1072 from frame 110 to 134, so its depth is constant there. It leaves the left end of the island at about frame 138, is in free
flight from about frame 138 to 191.3, then lands and rolls on the floor. On the floor its top edge stays at 1710-1713 from frame 206 to 278,
so its depth is constant there too. Its size is about 63-65 px throughout. The motion is therefore in a fronto-parallel plane with one m/px scale.

## Tracking
Background differencing (median background or last frame) plus a red HSV mask gave a silhouette per frame. From that I took the
centroid, the bbox and an ellipse fit. Overlays were checked visually.

## Scale from gravity
I fitted a quadratic to the flight track over frames 150-190: a_px = 6375 px/s^2 (centroid). Other features and windows
(bbox centre, ellipse centre, top edge, red-mask centroid, 141-191, 146-190) gave 6337-6435. I used s = 9.8/6375 = 1.537e-3 m/px.
A model with a depth-change term was ruled out: the counter and floor segments show no depth motion, and the parabola fitted to
frames 150-190 predicts the frames 141-148 red-mask track within 0.5 px.

## Answers
- 311 apple diameter: silhouette width/height 62-66 px (area-equivalent about 63, frame-0 extent 65). I used about 64.4 px, giving **0.099 m** (medium confidence, +/-3%).
- 312 table height: the apple's drop at constant depth. Centre at the parabola vertex is y=1104.3 (equal to the resting centre on the counter).
  The resting centre on the floor is 1745.2. The top-edge drop gives 639.5 px. Using 640 px gives **0.984 m** (high confidence).
- 313 horizontal speed in the air: vx = 431.5-433 px/s from the flight fits, giving **0.664 m/s** (high confidence). Rolling speed on the counter was 441 px/s, slightly higher because of pivoting at the edge.
- 314 horizontal distance of the parabola: from the vertex/edge (frame 137.5, x=380.5) to landing (frame 191.35, x=187.0) is 193.5 px, giving
  **0.297 m**. A cross-check gives vx*sqrt(2h/g) = 0.664*0.448 = 0.2975 (medium-high confidence; definition of the start point is +/-2%).
