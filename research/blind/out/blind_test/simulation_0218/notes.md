# simulation_0218 notes
Static camera, level (horizon ~y=540), robot translates left->right at 5.924 m/s.
Template matching (frame 24 crops, frames 16-32) gives per-part pixel speeds: track/wheels 50.8 px/frame,
body side 51.8, handle/redbox ~49.7-51.5, arm/drill 54.4 (arm sticks toward camera). Scale at each depth plane
= (5.924/24)/v_px m/px (pure translation, so independent of origin convention). Pinhole with cx=960, cy=540.
- 637 length: back of track x=798 (track plane 0.004859 m/px) to drill tip x=1447 (arm plane 0.004537) -> 3.00 m. Medium conf.
- 638 height: handle top y=271 (~0.00488) to track bottom y=897 (0.004859) -> 3.05 m. Medium conf.
- 640 tire: road wheel diameter ~70 px at track plane -> 0.34 m. Medium-low (which "tire" is ambiguous).
- 639 parking: camera height h=357 px*0.004859=1.735 m; ground scale at y: h/(y-540). Separators are perpendicular
  to wall (constant X), centres at X=-1.95 and +3.89 m -> spacing 5.84 m (along wall). Depth extent of space ~3 m for
  f~3200 (from paint-line width ratio), so the along-wall side is the long side. Medium conf.
