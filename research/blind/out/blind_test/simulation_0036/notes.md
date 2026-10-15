# simulation_0036 - boat + walking person (S3MC), 1080x1080, 72 frames @24 fps

## Scene
Fixed camera. Red fishing boat "AH805" moves left and toward the camera (range 133.96 -> 131.26 m between t=1 and t=2,
so range rate -2.70 m/s), with the bow leading. A person walks right along a sand bank at constant range (139.10 m).
No camera roll: the far shoreline is level. The horizon (the image row at camera height) is near y=690, because the
bow-top row of the hull stays fixed at y=690 while the boat approaches.

## Focal length (the key unknown)
- Rigid-body fit of the hull extremes (bow tip, stern) using L=10 m, plus 7 tracked cabin vertical edges, with the
  depths and heading = velocity: f ~ 3030-3075.
- Fit of the cabin edges alone (no 10 m prior; perspective rotation of the wheelhouse front face, cabin symmetric on the
  centreline): f ~ 2950-3050.
- Rate of change of the front-face width (-tan(theta) * LOS rate) with heading = velocity: f ~ 3090-3140. The side-face
  rate (+0.019/s) matches the prediction v_rad/Z = 0.020/s, which confirms that heading = velocity.
- Human-height plausibility (41 px at Z=137.9 m): f=3100 gives 1.82 m, f=3150 gives 1.80 m.
- Chosen f = 3100 px (horizontal FOV about 19.7 deg). Uncertainty is about +-4%.

## Measurements
- Boat: pixel motion of the hull mid fits (x-cx)*D = linear in t, so the velocity is constant. v_x = 9586/f = 3.10 m/s,
  v_z = 2.73 m/s, |V| = 4.13 m/s.
- Boat height: mast-top knob at y~542.5 to keel/rudder bottom at y~764 at t=1 (221.5 px). The hull sits on the water
  (the propeller is visible), so the visible bottom is the bounding-box bottom. Height = (74*132.4 + 147.5*133.4)/f = 9.5 m.
- Person: height about 41 px (mask extents 40-41 px while walking), so 41*137.9/3100 = 1.82 m. Pixel speed 25.1 px/s,
  with a small drift of +2 px/s downward and a range-preserving depth component. 3D speed = 1.11 m/s.

## Answers (confidence)
- 1149 boat height 9.5 m (medium: scales with f; also assumes the mast is part of the bounding box)
- 1150 person height 1.82 m (medium)
- 1151 boat speed 4.13 m/s (medium-high; only the lateral part depends on f)
- 1152 person speed 1.11 m/s (medium)
