# simulation_0017 - measurement notes

Video: 1080x1080, 101 frames, 33 fps. The frame is stored rotated 90 deg CW, so every frame was rotated CCW to get an upright view.
Fixed camera. Column edges are perfectly vertical (no pitch or roll). The receding floor-tile seams meet at (540.5, 540.0), so the horizon and principal point are at the image centre and there is no lens shift.

## Focal length (person kinematics)
- Head-centre x track (background subtraction, frames 3-100) fits u(t) = (A+Bt)/(1+ct) with A=-528.6, B=251.8 px/s, c=0.0018 and rms 1.8 px.
  The person walks almost exactly parallel to the image plane. The head top stays at y~367 at every gait peak, so Z is constant.
  This shows the person depth is the Euclidean range: Z-depth would need a 10% change in Z, which is not seen.
- Pelvis is about 10-16 px behind the head centre.
- Route 1 (D0/D1 ratio, no speed): f = 893-898.
- Route 2 (speed 1.3 m/s + D0 or D1): f = 897-902.
- With a floor-root depth convention both routes give f ~ 881.
- Adopted f ~ 888 +- 10 (FOV ~ 63 deg).
- A square-tile assumption gave f ~ 854. That was rejected because the "seam" it relied on at y=815 is the bench edge.

## Camera height (three consistent routes)
- Planted near foot at t=0-0.36 s: sole edge at y=731, Z ~ pelvis Z - 0.13 m. This gives Hc ~ 0.97.
- Static depth_info read as optical-axis Z to the object centres:
  - pedestal 5.963 with base y=703.5 (seen through the gap between cushions; the person occludes it, so it lies beyond Z=4.6) gives Hc ~ 0.964.
  - bench 2.267 with the plinth slab (front y=965.5, top-back y=857.5) gives Hc ~ 0.962.
  - sculpture 5.962 is the same as the pedestal.
- Euclidean-to-centre fits the pedestal and sculpture but not the bench, so Z-depth was used for static objects.
- The panel depth (4.223) matches no visible panel. Every visible panel is about 11.8 m away, so that origin is offset and was ignored.
- Adopted Hc ~ 0.965.

## Answers
- 1083 person height: 364.5 px at Z = 4.64 (frames 4-8, head 367 to sole 731) gives 1.864, i.e. 1.86 (walking peak). Confidence medium-high.
- 1084 pedestal width: dark square block, front face 249.7 px wide, base at v=164 gives W = 1.523*Hc = 1.47. Confidence medium-high.
- 1085 pedestal height: dark block from y 601 to 703.5 gives 0.625*Hc = 0.60. Confidence medium.
  The light tapered slab is taken to be part of the sculpture asset: it matches the width of the sculpture's bowl, and treating it that way makes the Euclidean distance ratios consistent. If the slab belongs to the pedestal instead, the height is about 0.92.
- 1086 bench seat height: cushion top, bench seat assumed centred over the plinth (cushion back/front v = 157.5/212.5) gives 0.50. Confidence medium.
- 1087 bench length: board front face from x 11.5 to 1058.5 = 1047 px at Z = 1.90 gives 2.24. Confidence medium.
- 1088 sculpture height (excluding the pedestal):
  - Including the light plinth (tip y=296 at Z = 5.97): 2.00.
  - Metal only: 1.68.
  - Answer hedged towards the first value: 1.95. Confidence medium-low.
- 1089 art display panel height: top bar y=463.75, floor contact v~71.5 gives Hc*(1+75.75/71.5) = 1.98. Confidence medium; the panel's depth_info does not match its geometry.
