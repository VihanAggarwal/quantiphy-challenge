# internet_0022 - overhead office desk (3840x2160, 36 frames, dataset fps 25)

Camera static (phase correlation on shelves/background < 0.3 px drift). Near top-down view with slight forward tilt
(table side edges diverge ~0.1 px/px toward bottom => ~1-2 % scale variation between rows; ignored, as GT is 2D pixel-scale).

## Scale
Apple Magic Mouse width = 57 mm. Edge profiles perpendicular to the mouse axis (frames 0,10,35): width 102-103.8 px
(mask minAreaRect 103.4 x 198.6 px). Using 103 px -> 0.5534 mm/px.
Check: white keyboard minAreaRect 501 x 212 px -> 277 x 117 mm (Apple Magic Keyboard 279 x 115 mm) => scale confirmed at table level.

## Measurements (frame 35 unless noted)
- Tea cup: circle fit to outer rim edge, d = 182.6 px -> 101 mm (tea surface 166 px). Answer 100.5 mm. Conf: medium-high.
- Saucer: circle fit d = 252.1 px -> 139.5 mm. Conf: high.
- Pencil: axis intensity profile, tip-to-end ~319 px -> 176 mm. Conf: high.
- Man shoulder width: jacket mask outline, shoulder tips ~860-900 px apart (y 400-450) -> 47.6-49.8 cm; frame 0 similar.
  Shoulders are ~0.4 m above table (closer to camera) so the real width is smaller (~40 cm); answer 47 cm (pixel-scale, slight hedge). Conf: medium.
- Table length: top edge corners (129,772)-(3489,808) = 3360 px -> 1.86 m; at mouse row width ~3455 px -> 1.91 m. Answer 1.88 m. Conf: medium-high.
- Monitor (iMac seen from above, top edge): ends (1937,2075)-(3115,1607) = 1268 px -> 70.1 cm pixel-scale.
  The top is ~45 cm above the table, so the real width is likely a 21.5" iMac (52.8 cm); GT assumed pixel-based; answer 69 cm. Conf: low-medium.
- Grey notebook: edge-fitted quadrilateral sides 239/244 px and 370/384 px -> width ~13.2 cm, length ~20.6 cm
  (consistent with a 13 x 21 cm notebook). Conf: medium-high.
- Hand (man's right hand, image left) 0.40 s -> 1.00 s = frames 10 -> 25: skin-mask centroid (931,1311)->(1455,1234) = 530 px;
  visual blob centres (912,1295)->(1462,1217) = 556 px; path length ~559 px. Using ~550 px * 0.5534 / 0.6 s = 50.7 cm/s.
  Answer 51 cm/s. Conf: medium (motion blur at frame 25).
