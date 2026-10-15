# simulation_0220 notes
Fixed camera, nearly level (horizon y0=551, VP x=959 from two parking-divider lines). Robot walks left at constant depth (feet bottom ~966-968 px).
- Robot centroid track (bg subtraction, frames 0-49): linear fit 204.9 px/s -> scale s = 0.82/204.9 = 0.00400 m/px at robot depth.
- Camera height h = s*(y_foot - y0) = 0.0040*416 = 1.665 m (scale units).
- Parking space: dividers at x~584 and ~1710 (row 875) -> 1125.7 px; same 5.78 m at rows 843 and 908 (consistent).
  W = 1125.7 * h/(875-551) = 5.79 m. This horizontal side is the long side (parallel stalls; depth side ~1.5-2.5 m for plausible f).
- Robot height: head top 654 to sole 966 (frame 48, upright) = 312 px; 306 px mid-stride frame 0 -> ~309 px * 0.0040 = 1.24 m.
Confidence: 647 medium (depends on long-side interpretation), 648 medium-high.
