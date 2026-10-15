# simulation_0124 — notes

Scene: 2D top-down Blender render (1080x1080, 72 frames @ 24 fps). Grey/red striped car (Mustang-like) and black car (911-like)
drive down a winding road; black car ahead/right of red. Frame 0 is an exact duplicate of frame 1. Both cars leave the frame
by about frames 47 (black) and 60 (red).
Prior: speed of black car = 26.085 m/s.

## Method
- Background = median of frames 62-71, which contain no cars.
- Tracking: rotation-aware template matching with car-aligned patches (work/tracker.py, tracker2.py chained; medtrack.py with a
  drift-free median car template). The two trackers drift in opposite directions along the car axis (about 0.05-0.1 px/frame,
  checked against the rear-edge position), so I averaged them. Frames 1-3, where the cars are cut off at the top border, use
  masked NCC (early.py / early2.py, two independent references). Both gave the same frame-1 distance (89.0-89.3 px).
- Camera is effectively orthographic. The median car image stays sharp across the image (no roof/bumper parallax), and the red
  car's pixel speed is constant everywhere, so one uniform scale applies.
- Pixel speeds: red is constant at 22.22 px/frame. Black rises slightly, from about 26.7 to 27.3 px/frame; it is 26.9 at
  t = 1.0 s, and 26.9 is also the mean. Scale k = 26.085/(26.9*24) = 0.04040 m/px.
- Dimensions come from car-aligned median images and from per-frame edge profiles, using frames where the sun shadow does not
  touch the measured side (the shadow falls ahead or to the left of each car).
  - Red: L about 121.5 px (rear -60.5, front +61). Body width 47.2 px; mirror-to-mirror 51.3 px.
  - Black: L about 113.5 px (rear -57.2, front about +56). Body width about 46-47.8 px; mirrors not visible (dark on dark).
  - The bounding box may or may not include the mirrors, so each width answer is set between body and mirror width (about 4% from each).
- Distances are centre to centre (body centres from the edge analysis). At frame 24 the distance is 105.1 px; at frame 25 it is
  107.0 px. Because frame 0 duplicates frame 1, I used 106.0 px to cover a one-frame offset. The minimum distance is at the
  start of the clip (frame 0 = frame 1), 89.1 px. The local minimum around frames 20-22 is about 102 px.

## Answers (confidence)
- 271 red speed at 1.0 s: 22.22*24*k = 21.55 m/s (high; the red/black speed ratio is robust; scale uncertain by about 1.5%)
- 272 red length: 4.91 m (medium-high)
- 273 red width: 1.99 m (medium; body 1.91, with mirrors 2.07)
- 274 black length: 4.59 m (medium; low-contrast edges)
- 275 black width: 1.97 m (medium-low; body about 1.88, with mirrors about 2.06)
- 276 distance at 1.0 s: 4.28 m (medium-high)
- 277 smallest distance: 3.60 m (medium; assumes the frame-0 state equals the frame-1 state)
