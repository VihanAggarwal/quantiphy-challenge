# simulation_0041 - boat + walking person on a beach (S2MC, 24 fps, 1080x1080, 72 frames)

## Scene / camera
- Static Blender camera, strongly oblique (not top-down): telephoto, looking down ~52.6 deg.
- Camera recovered with a pinhole model (pp = image centre, no roll):
  - Vertical VP from mast + cabin corner edges tracked over 66-72 frames: (453,5045)/(437,5113); x-offset explained
    by ~0.65 deg bow-up trim of the boat (roof edge slope 0.287 vs motion slope 0.280) -> true VP ~ (540,5082), d=f*cot(a)~4540 px.
  - Horizon distance from the boat's perpendicular image-scale change while translating (feature-pair separations shrink
    1.33-1.5 % over 71 frames, bundle fit of pure-translation model with template tracks: h_d=f*tan(a)~7800 px).
  - => f ~ 5900 px (FOV ~10.5 deg), alpha ~ 52.6 deg (range 52.2-53.3). Cross-check: green-hatch edge (beam direction)
    image slope -0.393 matches the model's predicted -0.394.
- Scale: person height. Ground point under the head from the shadow-axis/vertical intersection; head-top silhouette at
  mid-stance = 37.3-37.4 px above it (toe-based check agrees). Head-silhouette offset (+~0.04-0.05 m) -> 37.4 px <-> ~1.79 m.
  Camera height ~139 m, person depth ~173 m, ~34 px/m horizontal at the person.
- First two video frames are identical (motion starts at frame 1).

## Measurements
- Boat speed: template-tracked features back-projected at their heights; constant velocity; 4.04-4.05 m/s
  (range 3.98-4.08 over camera solutions). Image speed ~5.9 px/frame.
- Person speed: head-top track back-projected at 1.75 m and shadow ground point; mean 1.39 m/s, local fits around
  t=1.0 s 1.41-1.43 m/s.
- Boat length: bow tip (stem head) to stern end, back-projected with sheer heights, projected on heading:
  9.78-9.85 m across 7 frames (9.67-9.91 across camera solutions).
- Boat width: symmetric gunwale chords (near red->white gunwale vs far deck edge) along the beam direction: 2.92-2.95 m at
  the last visible station before the cabin (still widening); extrapolated max beam ~3.1-3.2 m.
- Assumes boat long axis is world-axis aligned (AABB = own length/beam).

## Answers / confidence
- 11 length 9.8 m (medium; scale/alpha +-4 %)
- 12 width 3.1 m (low-medium; beam vs height ambiguity, extrapolation)
- 13 boat speed 4.03 m/s (medium)
- 14 person speed 1.41 m/s (medium-low; gait oscillation of pelvis)
