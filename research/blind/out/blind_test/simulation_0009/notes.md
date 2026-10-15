# simulation_0009 — boat, pier, cabin stairs (Blender, static camera, 1080x1080, 24 fps, 66 frames = 2.71 s)

## Camera model
- Static camera, verticals vertical (no roll, ~zero pitch). Horizon from VPs of horizontal lines:
  cabin eave/platform -> (1588,540); pier front edge x its reflection -> (1559,550); boat-track FOE consistency
  and LK depth-rate fits -> 535-550. Adopted horizon/cy = 545 (spread 540-550 drives most of the uncertainty).
- Right VP (pier long axis, cabin long side) x~1593 at y=545; boat FOE from bow-tip track x~-261, which equals the
  pier short-axis VP (pier caps/cabin gable lines -270..-350) -> boat moves parallel to pier short axis (world axis).
  f = sqrt((540-xL)(xR-540)) ~ 918 px (HFOV ~61 deg); range 895-942.
- Depth convention: Euclidean range fits (Z-convention would need f~1500 and put the origin in front of the stern).

## Scale
- Boat speed 1.5 m/s along d (FOE direction): image depth rates b = vz/Z per tracked point from v(t)-cy = K/(1+bt)
  (bow tip b~0.090, stern waterline b~0.110, stern rail LK point b~0.1135 at cy=545).
- Stern waterline (blue hull -> green reflection colour transition) at v=862 at t=0 gives camera height above water
  H = (862-cy) Z/f ~ 3.55 m (b-based). Requiring the boat origin (O.d = (D1^2-D0^2-1.5^2)/3 = 10.30 m) to sit at the
  boat's mid-length gives H ~ 3.49; with the same H the pier deck-centre distance = 18.93 m vs given 18.920 (check).
  Adopted H = 3.49 m.

## Measurements / answers
- Boat length (bow post tip -> stern rail along axis): 3.59 (centred-origin scale) .. 3.65 (b-scale) + ~0.1 stern
  rounding -> 3.65 m. Medium confidence (+-7%).
- Boat width: rim outline unprojected to gunwale plane (0.5 m above water): far rail l~5.73, near rail l~4.43 -> 1.30 m.
  Medium confidence.
- Boat height: bow post top ~0.92 m above water; keel not visible (submerged) -> assumed draft ~0.13 m -> 1.05 m. Low confidence.
- Pier: end face top v=705.5, its reflection gives waterline v=728.9 -> deck height = 23.4/(728.9-545)*H = 0.44 m.
  Deck width (back-left corner to front-left corner on deck plane) 1.68 m (post centre spacing 1.47 m consistent);
  length water end -> visible shore end (x~563) 5.36 m -> 5.4 m. Medium confidence.
- Min distance pier outer end to boat at t=3 s (extrapolated 4.5 m along d): boat alongside the pier end;
  lateral gap from pier end face (l=7.96) to boat's starboard rail (l~5.73) ~2.22-2.25 m. Medium-low confidence
  (answer would be ~3.1 m if measured origin-to-end-centre).
- Stairs: bottom corners (608.6,660),(667,667.5), top (700,619), rail top (699.3,585); ground height solved so the
  stairs bbox centre is at 23.125 m -> ground ~0.6 m above water; width 1.91 m, rise (cabin floor above ground) 1.08 m.
  Door height check ~1.94 m (plausible). Medium confidence (f-dependent +-3%).

## Scripts
track.py/tm3.py (feature tracks), fit*.py/scen.py/final.py (models), wl.py (waterline), pierlines.py/eave.py (VPs).
