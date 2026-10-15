# simulation_0009 — boat passing a pier, cabin with stairs (66 frames, 1080x1080, fps 24)

## Camera
- Level camera: horizon at y~539 (VP of pier/cabin long axis at (1653,540) from ~24 LSD lines; boat FOE (-265..-278, 535..539)).
- Focal length f ~ 1000 px (HFOV ~57 deg). Evidence: pier cap columns VP2 ~ -365 (f~1004 with VP1); boat thwart lines VP ~1825 with
  boat motion FOE ~ -270 orthogonal at f~1020; stairs treads / porch fascia VP2 ~ -300 (f~960). Pier/stair answers are anchored by
  their own ranges, so they are only weakly f-sensitive.
- Water plane: camera ~3.3 m above water (pier-centre range 18.92 with deck geometry: 3.34; boat r0-anchored reconstruction: 3.27-3.31).

## Boat (prior 1.5 m/s, r0=11.827, r1=13.154)
- Tracked 63 LK features + bow-post / stern tips; projective fit u(t)=F+(a-F)/(1+lam t) gives FOE and per-point inverse TTC.
- 3D from depths z=Vz/lam, rescaled (k~0.93) so the bbox centre has range 11.827 (speed-based scale is ~7% larger; range-based chosen
  because it agrees with the pier-based water height). Rightmost stern point is the far transom corner (~0.35 m off centreline).
- Length (bow-post tip to transom) ~3.1-3.25 m; boat heading ~4 deg off the pier axes so world-AABB length ~3.23 -> answer 3.2.
- Beam from lateral feature span ~1.2 m; world-AABB (if pier = world axes) ~1.42 -> hedged 1.3.
- Bow-post top ~0.89 m above water + ~0.1 m draft -> height ~0.97 m.

## Pier (distance 18.92 m to its origin, assumed deck centre)
- Mirror geometry of end face & posts: deck top 0.124*h_w above water -> 0.41 m.
- Deck corners on the deck plane: width (back-left 296.5,705 -> front-left 342,717) ~1.56-1.58 m; length to visible shore end (561,688)
  ~4.8 m, range-consistent length ~5.2 -> 5.0 m.

## t=3 s distance
- Boat origin extrapolated at 1.5 m/s along FOE direction; at t=3 the pier's outer end is abeam of the boat centre, 2.6-3.0 m
  laterally; minus half beam (~0.6) -> ~2.3 m (would be ~2.85 if measured to the boat origin).

## Stairs / cabin (stairs distance 23.125 m)
- Stringer foot (665,668) on ground, top (699.5,618) at porch floor, run along cabin long axis: rise ~1.05 m, run ~1.19 m,
  ground ~0.5 m above water.
- Tread length between stringers ~46 px (1.36-1.43 m), outer stringer-to-stringer ~60 px (~1.75 m) -> 1.5 m.

## Confidence
Pier width/deck height: medium-high. Boat length/height, cabin floor height: medium. Boat width, stairs width, pier length,
t=3 distance: medium-low (definition ambiguity: AABB vs intrinsic, surface vs origin).
