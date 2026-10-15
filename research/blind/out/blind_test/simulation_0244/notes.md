# simulation_0244 (V2MC, 30 fps, 1080x1920, 75 frames; static camera)
Scene: ibex-like "antelope" and a rabbit both walking left->right across a road at the same depth
(hooves / rabbit feet both at y~1545-1548). Prior: antelope speed 1.277 m/s.

Scale: antelope pixel speed from template tracking (torso chained 6.49, neck 6.45, drift-free shoulder
matches ~6.6 px/frame) -> 6.55 px/frame = 196.5 px/s -> 0.0065 m/px at antelope/rabbit depth.

- 820 antelope height: horn top y~1128-1136 to hooves ~1545 -> ~417 px -> 2.71 m (medium-high conf).
- 821 antelope length (nose to tail tip, tail pose varies 400-460 px over frames 0/20/38/66, mean ~430 px) -> 2.78 m (medium).
- 823 rabbit speed: bg-subtracted mask centroid fit 6.70 px/frame (vs antelope 6.55) -> 1.306 m/s (high).
- 824 rabbit height: ears top 1482 to feet 1548 -> 66 px -> 0.43 m (medium).
- 825 rabbit length: 68-82 px depending on hop pose, ~72 px -> 0.47 m (medium).
- 822 left tree height: top y~365; base hidden behind roadside bushes. Horizon estimated ~1330-1370
  (mountain foot ~1390, receding right shrub row). Tree depth ratio vs antelope ~1.4 from haze (dark-level)
  comparison -> base y~1490 -> 1120 px * 0.0065 * 1.4 ~ 10.2 m (LOW confidence; range 8.5-13 m).
