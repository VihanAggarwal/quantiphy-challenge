# simulation_0031 - notes

Scene: fixed narrow-FOV camera looking down (~13 deg) at a beach; red/white fishing boat moving away-left,
person walking left/toward camera on sand, bald eagle flying toward camera-right. 960x960, 75 frames, fps 24.

## Key finding: human depth_info is inconsistent
Person image velocity (template track, 3 s): (-28.9, +14.2) px/s. If depth_info for the human were right
(range ~const 139.95->139.98) the 1.3 m/s prior would force f~3435 px (person ~3.1 m tall, eagle span ~3.4 m)
AND the person would have to descend ~0.5 m/s. That hypothesis was rejected because:
- boat divergence (mast band shrink 2.06+-0.3 %/s; image deceleration k=0.025/s) matches the BOAT depth rate (2.4 %/s),
  giving a horizon 1415 px above centre (boat moves horizontally); the eagle's depth+track is exactly level flight
  with the same horizon -> horizon robust.
- wheelhouse edges: window-face edges point to the boat FOE (slope 0.455 vs 0.457 predicted); door-face (transverse)
  edges slope -0.1325+-0.008 -> orthogonal-VP focal length 6380-6590 px (f=3435 would need slope -0.40).
- mast tilt trend vs x (nadir VP) -> f ~5880 (+-200 stat, heel-sensitive).
- person height increases 74->76 px over the clip (approaching ~1.2 m/s), consistent with a flat/slightly downhill walk
  at 1.3 m/s, not with constant range.
Chosen f = 6220 px (FOV 8.8 deg), pitch 12.8 deg, pp at centre, roll 0. Person range taken as ~140 m.

## Measurements / answers
- 1123 person height: 75 px (74-76) head-top to sole at R~140 -> 1.73 m (f 5900..6550 -> 1.84..1.64). conf medium.
- 1124 boat height: mast top (y=434 @t=1) to underwater rudder bottom (y=912), reconstructed on the centre-line plane
  through the mast (range 130.35) -> 8.96 m. conf medium-low (draft through water, f).
- 1125 boat length: bow tip -> stern rim 9.54 m, -> rudder 9.85 m; answer 9.7 m. conf medium.
- 1126 boat width: near/far gunwale pairs along the transverse direction -> 3.1-3.25 m max beam; 3.16 m. conf medium-low.
- 1127 boat speed @1s: 3D displacement t=1->2 from depth (130.35->133.74) + image track (-87,-38 px), motion horizontal
  (check: vertical comp 0.00) -> 3.96 m/s (insensitive to f). conf high.
- 1128 eagle length: not directly measurable (body points at camera); 0.45 x wingspan -> 0.84 m. conf low.
- 1129 eagle speed @1s: frames 24/48 (same wing phase), depth 139.76->130.25 -> 11.58 m/s (level flight, heading exactly
  opposite to the boat). conf high.
- 1130 wingspan: max spread frames 5-6, 32-33 extent along wing axis 68-74 px at R 147/136 -> 1.86 m. conf medium.
