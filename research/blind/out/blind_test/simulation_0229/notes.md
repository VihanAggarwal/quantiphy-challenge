# simulation_0229 (classroom, paper airplane, static camera 1920x1080, 24 fps, 50 frames)
Scale: chalkboard outer frame x 321.5 -> 1692 = 1370.5 px = 5 m -> 0.003648 m/px at wall depth.
Camera: ceiling-line vanishing point (Hough, 41 lines) = (962, 539.3) -> zero pitch/yaw, wall frontal.
Depth of floor objects relative to wall from floor-contact rows: Z/Zwall = (951.5-539.3)/(y_floor-539.3); wall-floor junction y=951.5.
- 715 clock: outer ring 113 px (1704.5-1817.5 x, 235.5-349 y) -> 0.412 m (high conf).
- 716 board height: frame top 296, frame bottom 737, chalk tray to ~745 -> 444 px -> 1.62 m (1.61-1.64) (med-high).
- 717 right chair by board: backrest 1600.5-1751.5 at back-leg floor y~997, seat-front/front-right leg at 1790 (floor y~1020); world X span 2.10..2.59 -> 0.50 m (medium).
- 718 teacher desk: top slab 71.5-771.5 px (700 px), front face 90-751.5, front-face floor y=999.5 -> Z ratio 0.8957 -> 2.287 m (medium).
- 719 ceiling: ceiling-wall junction y=174, floor-wall 951.5 -> 777.5 px -> 2.837 m (med-high).
- 720-723 plane: background-subtraction blob track frames 16-32 (visible vs board), constant apparent length (~133-139 px) -> constant depth; board scale assumed (2D video).
  Backward-diff speeds 6.70 (f17) -> 5.15 (f32) m/s; local linear fits: v(1s,f24)=6.07, a=-2.8..-3.4; v(1.25s,f30)=5.35, a=-2.6..-3.1. Answers magnitudes. Medium conf (plane depth vs board unknown).
