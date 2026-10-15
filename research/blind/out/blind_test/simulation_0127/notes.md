# simulation_0127 — notes

Scene: nadir (top-down) Blender camera over a street, 1920x1080, 24 fps, 57 frames (frame 0 duplicates frame 1).
Bike moves left at constant speed; blue car moves right at constant speed (starts partly under a tree);
red car (far left) and dark-green sports car (far right) are parked. Red and blue cars are the same sedan model
(same window/sunroof/hood-vent layout and identical measured length).

## Scale (prior: bike speed = 24 m/s)
- Median background + difference images, template matching, sub-pixel edges.
- Bike pixel speed depends on feature height (perspective): body template (rider torso) 31.77 px/frame,
  thin leading edge (front wheel) 31.37, shadow on the ground 31.24-31.34 (tip template and centroid).
  Ground-level bike speed taken as 31.27 px/frame, giving g = 24/(31.27*24) = 0.03198 m per ground-level px.
- Parallax check: blue-car roof template 25.56 px/frame vs rear-bottom edge 25.19 px/frame (ratio 1.0147).
  With sedan proportions this gives camera height ~65-85 "car metres" (f ~ 3900 px, HFOV ~ 28 deg). Height
  corrections on silhouettes are 1-3%.
- No motion blur (moving edges are as sharp as static ones).

## Measurements (image px -> ground px after height correction -> m)
- Blue car speed: rear-edge track 25.19 px/frame (frames 5-38), roof 25.56; ground speed ~25.11 px/frame
  -> 24*25.11/31.27 = 19.27 m/s (cross-check using roof vs bike body: 19.31). Constant speed. Answer 19.3.
- Sedan length: red 13.5->255.5 (242 px), blue 241.3 px mean over frames 12-28; corrected 237.3 ground px both
  -> 7.59 m. Answer 7.6 for both cars.
- Sedan width: body 715->805 (red, 90 px) ~ 88.5 ground px = 2.83 m; including mirrors 710.5->808.5 (98 px)
  ~ 96 ground px = 3.07 m. Blue car consistent (body ~86.5-89, mirrors ~95). Unknown whether the dataset AABB
  includes mirrors, so answered the midpoint ~2.95 (within ~4% of either).
- Green car: x 1685.75->1916 (230 px), y 719->811.5 body, mirrors 716.5->818. Rear end is the outer end (offset
  ~955 px), so a 5-10 px perspective correction: length 220-225 ground px -> 7.04-7.20 m, answer 7.14.
  Width body 91.8 ground px = 2.94 m, mirrors 100.2 = 3.20 m -> midpoint 3.07.
- Bike length: thin line in top view, front wheel front to rear wheel back, rows above the wheel shadows:
  85.2 px median over frames 16-36 -> 84.8 ground px -> 2.71 m.

## Confidence
- 287 blue car speed: high (+-2%).
- 289/292 sedan lengths: high (+-2-3%).
- 290 bike length: medium-high (+-4%, thin features at the ends).
- 294 green length: medium (+-4%, low contrast and a large perspective correction at the frame edge).
- 288/291/293 widths: medium (mirror inclusion ambiguity of ~8%, hedged at the midpoint).
