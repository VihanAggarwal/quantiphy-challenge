# internet_0005 (Solna-style metro station, woman in yellow walks left->right along far wall)
Static camera, 854x480, 178 frames @25 fps. Treated as 2D/planar (no depth_info): one m/px scale at the woman's plane.

## Scale
- Median-background subtraction track of the woman (frames 0-140): centroid 54.68 px/s, head 55.03, yellow torso 54.03 -> 54.7 px/s.
- Scale = 1.25 / 54.7 = 0.02285 m/px.
- Floor tile joints converge to VP (424, 304.3) -> horizon y=304.3; woman's feet at y~375.5 -> camera height ~1.63 m (plausible eye level), consistent.

## Measurements
- 2165 signs: left sign/post centre x=327.5, right x=538 -> 210.5 px -> 4.81 m planar (= 1.25 m/s x 3.85 s the woman needs to walk from sign to sign).
  Signs stand at wall base (post foot y~362.5) slightly behind the woman; full 3D would give ~5.9 m. Answer 4.9 (slight hedge). Confidence medium.
- 2166 woman height: head top ~300.4 (mid-stance), shoe bottom ~375.5 -> 75.1 px -> 1.72 m. Confidence high.
- 2167 light above head: lowest light row (y~250, directly above her path in image; e.g. frame 88 she is right under one) FWHM 46 px -> 1.05 m;
  other rows (y 177/195/236) ~56-59 px -> 1.28-1.35 m. Answer 1.09 (leans to y=250 row). Confidence low-medium.
- 2168 floor tiles: joint spacing along far tile row fits spacing = 0.751*(y-304.3); at woman's foot row 53.5 px -> 1.22 m. Confidence medium.
