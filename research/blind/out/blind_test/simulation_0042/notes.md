# simulation_0042 — eagle + fishing boat, fixed oblique aerial camera (1080x1080, 24 fps, 72 frames)

## Camera
- Static camera (background identical across frames). Video frames 0 and 1 are duplicates; t = frame/24.
- Focal length from the eagle speed prior: eagle trend positions (linear+quadratic trend + flap-periodic terms fitted to
  blob centroids; flap period ~24.2 frames) at frames 24/48 = (367.6,467.5)/(760.1,571.1), 406 px apart.
  |r2*ray2 - r1*ray1| = 11.84 m  =>  f = 6211 px (HFOV 9.9 deg). Constant eagle velocity verified: predicted pixel-speed
  growth from perspective (+2.5%/s) matches the observed one.
- Pitch: boat moves on the water plane, so (B2-B1) is horizontal. With roll = 0 (verticals look vertical):
  theta from nadir = 34.4 deg (range convention) / 37.2 deg (z-depth convention). Eagle-level flight would give 36.5/36.0 deg;
  both conventions are near-consistent (eagle climbs +0.15 m/s or sinks -0.05 m/s). Used a blend; differences < 2.5%.
- Boat heading = motion direction (cabin roof edge 15.1-15.3 deg in image vs motion 15.7 deg). Eagle flies antiparallel
  to boat (0.2-0.8 deg), so both move along a world axis -> AABB dims = object dims.

## Measurements (frame 24, boat range 177.2 m): image Jacobian per metre: |pX| 34.5 px, |pY| 30.7 px, |pZ| 18.7 px
- Boat speed: template-matched boat displacement (-136.2,-38.25) px per 24 frames (uniform), ranges 177.2077 -> 177.9993
  => |B2-B1| = 4.11 (range conv) / 4.14 (z conv) m/s. Answer 4.12 m/s. Confidence high.
- Boat length: bow tip x=216.3 to stern silhouette x=546 (50% edges) -> du = 329.5 px; corrected for stern rounding
  (dY~0.5 m) and sheer (stern deck ~1.5 m lower) => 9.70-9.75 m. Answer 9.72. Confidence medium-high (+-2%).
- Boat width: port gunwale (white/red boundary) vs starboard gunwale chords along projected Y axis; centreline drift
  (sheer) fitted from symmetric chords forward (xi 20-92) and aft (rails); max half-breadth 48.3 px at ~43% length
  => beam 96.5 px => 3.12-3.20 m. Answer 3.16. Confidence medium (+-5%, mid-ship starboard edge hidden by cabin).
- Eagle length: beak-tail extent along flight direction at 50% contrast ~27.7 px (26.5-28.5) at r~179.6
  => 0.82 m (0.79-0.85). Confidence medium.
- Eagle wingspan: max tip-to-tip extent perpendicular to flight, frames 53-55 (wings straight) ~60-61 px at r~176.6
  => 2.04-2.14 m; arched-wing frames (31) give 1.9 m. Answer 2.05. Confidence medium.
