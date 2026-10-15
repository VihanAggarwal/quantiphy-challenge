# simulation_0130: notes

**Scene:** static top-down camera over a hangar floor, 1920x1080 at 24 fps, 72 frames (frames 0 and 1 are identical).
- The "car" is a forklift-like vehicle (yellow forks in front, black overhead guard, rounded counterweight at the rear). It drives up the image at a constant speed.
- A white A320-type airliner follows directly behind the car and moves at the same pixel speed.
- A Mi-24-type helicopter sits still on helipad "02". It has 5 static rotor blades and a nose probe.

## Scale
- Car track from template matching with subpixel peaks, frames 1-71. It is linear at 5.2486 px/frame, which is 125.97 px/s. The quadratic term is negligible.
- k = 11.155 / 125.97 = **0.088555 m/px**.

### Projection check
The camera behaves orthographically, so one scale applies to the whole frame. Two checks support this:
- The airplane's pixel speed (5.2459 px/frame) matches the car's to within 0.05%, although the tracked features sit at different heights. A perspective camera at a few hundred metres would give a difference of about 1-2%.
- The fin of the airliner projects exactly onto the fuselage centreline, with no radial lean.

### Sanity check
At this scale the airliner is 37.6 m x 34.3 m, which matches the real A320 (37.57 m long).

## Measurements
Edges are half-level crossings, taken across many frames or from median-aligned stacks.

| qid | quantity | pixels | answer |
|---|---|---|---|
| 301 | car length (fork tips to counterweight; forks counted as part of the vehicle) | 72.1 | 6.385 m |
| 302 | car width (mast/fender and counterweight width) | 23.9 | 2.116 m |
| 303 | airplane length (nose to tail cone), median over frames 52-71 | 424.5 | 37.59 m |
| 304 | airplane width (wingspan), median over frames 52-71 | 387.15 | 34.28 m |
| 305 | helicopter length (nose probe tip at y=176.1 to tail fin at y=600.3) | 424.2 | 37.57 m |
| 306 | helicopter width (rotor blade tip to blade tip, x=1284.7 to 1619.6) | 334.9 | 29.66 m |
| 307 | airplane speed at 1.0 s (towed rigidly with the car; measured ratio 0.9995) | — | 11.155 m/s |

## Confidence
- **303, 304, 307:** high.
- **302:** medium-high.
- **301:** medium. If the bounding box excluded the forks the length would be about 4.46 m (50.4 px). The forks look like rigid geometry: they occlude the floor grid lines.
- **305:** high. The length is the same whether or not the rotors are included; without the probe it would be 35.9 m.
- **306:** medium. With the rotors excluded, the stub-wing span would be about 17 m.

The light "trails" in front of and behind the vehicles were ignored. They look like ground streaks, not part of the vehicles.
