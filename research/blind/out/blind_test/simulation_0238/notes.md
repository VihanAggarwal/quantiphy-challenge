# simulation_0238 (V2MC, two horses walking left->right in front of a half-timbered house, static camera, 1080x1920, 24 fps, 49 unique frames; frame 49 = frame 0)
- Brown horse = horse at back (hooves at y~1045 vs white ~1049; horizon y~986). Prior: brown speed 0.874 m/s.
- Brown pixel speed (HSV mask, centroid/torso/nose fits over frames 0-48): 77-81 px/s -> 78.5 px/s -> s_brown = 0.01113 m/px.
- White (front) horse: background-diff mask, front edge 145.6, rear edge 139.9, nose manual 141.5 px/s -> 143 px/s.
- Depth ratios from ground contact rows vs horizon 986: white/brown Z = 59/63 -> s_white = 0.01043; house wall (grass edge 1037) Z/brown = 59/51 ~1.15 -> s_house = 0.01280.
- Brown: height 162 px (ears to hoof), length 186 px (tail to nose). White: height 169 px, length 225 px.
- House: ridge y 259 to base ~1037 => 780 px; widest (lower eave) 729 px. Window 65.5 x 108.8 px.
Confidence: brown sizes medium-high; white speed/sizes medium (depth ratio); house/window medium-low (house depth ratio 1.0-1.16 uncertain).
