# simulation_0015 - atrium gallery, walking person (1.87 m), static camera, 1080x1080, 33 fps

## Camera model
- Level camera: VP of 12 long building lines = (539.95, 539.61) -> horizon y=539.5, principal point = image centre.
- f = 900 px (30 mm on 36 mm sensor). From the person: head-top peak over gait = (fh + 453)/f ~ 1.86-1.87 m.
- KEY FINDING: depth_info behaves like camera Z-depth (along the optical axis), not Euclidean range:
  * right freestanding panel R1 (x 946-1055) floor ends give centre Z = 11.82-11.85 vs given 11.874 (range would be 13.4 m, impossible under any consistent scale).
  * pedestal Z=9.46 consistent with square base (fh 1205); person feet at mid-stance -> fh 1222-1240.
- Floor model: Z = fh/(v-539.5), fh = 1222 -> camera height h = 1.358 m.

## Measurements
- Pedestal (grey square box): front face x 464.8-614.5 (149.7 px), rows 615.5-677.5; Z_front 8.73-8.86 -> width 1.45-1.47, height 0.60-0.61.
  A light tapered plinth sits on it (top ~0.93 m). Sculpture tip row 423.5 at Z 9.46 -> top Y = 2.58 m.
  Ambiguity: plinth may belong to pedestal (pedestal 0.93, sculpture 1.65) or sculpture (pedestal 0.61, sculpture 1.97) or be separate (0.61 / 1.65). Hedged: sculpture 1.73, pedestal 0.62.
- Panel R1 (nearest by Z): rotated ~33 deg; posts 1.05 m apart, base 1.15 m, top bar 1.21 m -> width ~1.18; floor to top bar 1.98-2.00 m -> 1.99.
- Benches (two, aligned with optical axis, X = -3.46 / +3.32): base plate side edges pass through VP; seat front at Z~8.6, back at Z~10.84-10.90 -> length 2.23-2.32 (2.27); front face width 0.70-0.72 (0.71); slab top 0.455 m, cushion top 0.505 m -> height 0.50.
- Roof frame: far member band rows 191.5-208.75 at back-wall plane (wall base row 578 -> Z 31.7 m): underside 13.0 m, thickness 0.61 (mid beam gives 0.56) -> 0.60.
- Bird: NOT visible in any frame (temporal std / frame differencing finds only the person and its floor reflection). 5.5 m/s is a pure prior guess.

## Confidence
1120 sculpture height 1.73 (medium-low: object split ambiguity), 1121 pedestal width 1.46 (high), 1122 pedestal height 0.62 (medium),
1123 panel width 1.18 (medium), 1124 panel height 1.99 (high), 1125 bench height 0.50 (medium), 1126 bench width 0.71 (medium-high),
1127 bench length 2.27 (medium-high), 1128 clear height 13.0 (medium), 1129 frame thickness 0.60 (medium-low), 1130 bird speed 5.5 (guess).
