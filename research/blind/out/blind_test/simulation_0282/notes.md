# simulation_0282 (V2SS, top-down dragon flying right-to-left, 2560x1440, 24 fps)
- Background = temporal median; dragon mask by diff. Head/tail tracked in central body band.
- Pixel speed: linear fit of head/tail x over frames 5-62 ~ 35 px/frame = 840 px/s -> scale 1.29/840 = 1.536e-3 m/px.
- Body length (snout tip to tail tip): 434-548 px over flap cycle (pose flex); straight-body frames ~520-548 -> 525 px -> 0.81 m (medium confidence).
- Wingspan: max vertical extent of mask with wings flat ~1030-1034 px (frames 0, 26) -> 1.58 m (medium; gliding pose gives 900 px = 1.38 m).
- Displacement 0.5-1.0 s (12 frames): 12*35 px = 420 px -> 0.645 m (head 394 px, tail 500 px; consistent with prior speed*0.5 s). High confidence.
