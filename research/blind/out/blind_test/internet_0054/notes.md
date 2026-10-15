# internet_0054 notes
- 3840x2160, 94 frames @30fps. Handheld camera, small drift (~29 px full-res over clip, measured by phase correlation on building).
- Rider tracked (white shirt mask, stabilized): linear, ~8.3 px/frame at half-res -> ~499 px/s full-res (raw unstabilized ~490). Scale = 4.9/495 = 0.0099 m/px.
- Note: implied scale is ~1.6x real-world (person 2.85 m); followed prior as the scale per instructions. Main risk: if GT uses real sizes, all answers ~1.6x high.
- Person: cap top y~817 to sole y~1105 = 288 px -> 2.85 m (med conf).
- Bench: 4 benches 267-281 px, mean ~275 px -> 2.72 m.
- Canopy (pergola incl. foliage): height 586 px (top foliage to ground) -> 5.8 m; width 1840 px -> 18.2 m.
- Scooter: handlebar top to wheel bottom ~190 px -> 1.88 m. Wheels outer extent 181 px (1.79 m), centre-to-centre 143 px (1.42 m); answered 1.65 as hedge.
