# internet_0051 notes
- Camera pans slowly: background shift +13 px over 48 frames (phase correlation on trees).
- Scooter front wheel x 1491 (f0) -> 661 (f48), y~855; relative to background 843 px in 1.6 s = 17.56 px/frame.
- Prior 2.07 m/s -> 0.00393 m/px at rider depth (ground y~855).
- Horizon ~y600 (Fiat roof ~ horizon for ~1.5 m camera; Jeep consistent). Ground-plane scale ratio: car row (y800) x1.275 -> 0.00501 m/px; tree base (y777) -> 0.00566 m/px.
- Person: head top 554 to sole 850 = 296 px -> 1.16 m (low confidence: real-world scale suggests ~1.7; prior implies smaller scene).
- Fiat (green): width 262 px -> 1.31 m; height 598-800 = 201 px -> 1.01 m.
- Tree: 75-777 = 702 px -> 3.97 m.
- Brown Jeep right edge ~775 to Fiat left ~1093 = 318 px gap -> 1.59 m (gap, not centre distance; centre-centre would be ~3.06 m). Low-medium confidence.
- Note: real-world dims (Fiat 1.63 m wide, wheelbase) suggest the prior speed is ~0.65x of what pixel motion implies; followed prior per instructions.
