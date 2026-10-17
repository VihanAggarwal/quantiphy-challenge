# sim2_06 independent remeasure: qids 1953, 1957

Question for both: "What is the spacing in meters between the markings on the pool wall?"
- 1953: simulation_0225_segmented. 1957: simulation_0227_segmented. The prior for both is cat speed = 1.041 m/s.
- In the segmented clips the background is removed, so the pool wall is not visible. Both segmented clips use the same camera and framing as their unsegmented twins 0225/0227: the chairs and cat sit at the same pixels.
- The "markings on the pool wall" are the vertical joint lines on the front (vertical) face of the pool coping. In the front view this face spans y=927..970, just above the water. These rows replace "pool tile width" in the unsegmented siblings' question lists.
- The 0225 and 0227 front views are the same camera. The wall marks sit at identical pixels in both, and the cat pixel speed is identical. The two answers must therefore be equal.

## Route 1 (front view, the question's own camera)
- Cat pixel speed: I matched the dark mask across frames at the same gait phase (gait period ~18.5 frames, lag 37 = two cycles, FFT cross-correlation with subpixel peak).
  - 0225_seg: 5.391 px/frame. 0227_seg: 5.389. 0225 orig (background subtracted): 5.397. 0227 orig: 5.397.
  - The speed is constant over the clip (lag-37 values 5.38-5.40 throughout). I used 5.392 px/frame = 129.4 px/s, giving 0.008044 m/px at the cat's depth.
  - The cat stays at constant image y with no size trend, so it walks parallel to the image plane.
- Wall marks (column minima of the band y=934-962, 10-frame mean): 332.8, 482.2, 632.9, 781.3, 930.8, 1081.9, 1232.3, 1381.9, 1532.6, 1681.0, 1830.6.
  - Linear fit pitch = 149.87 px, rms 0.66. The pitch is uniform across x, so the wall is parallel to the image plane.
  - 0227 gives the same positions.
- Depth ratio (level-camera ground plane, m/px proportional to 1/(y - y_h)):
  - Cat paw ground contact y ~917 (zoomed crops of several frames show planted paws at 915-918). Deck front edge / top of the wall face at y ~926.5.
  - The horizon is at y ~540-550. The deck-joint vanishing-point fit gave 547-553; the ratio barely depends on this value.
  - Ratio = (917-540)/(926.5-540) = 0.975.
- Spacing = 149.87 x 0.008044 x 0.975 = 1.176 m. The range for contact y 915.5-918.5 and horizon 540/550 is 1.170-1.181.
- Check: the deck paver joint lines meet y=922 with a pitch of 147.2 px. The wall pitch projected to that row would be 147.7 px, so the pavers and the wall marks share the same world pitch (the coping is staggered by half a paver).

## Route 2 (top-down siblings 0226/0228, same world)
- Paver joint pitch: 144.58 px (11 joints, 429.8 to 1875.6, same in both clips).
- Cat pixel speed (gait-matched): 5.446 / 5.447 px/frame.
- Spacing = 144.58 / 5.446 x 1.041 / 24 = 1.152 m on the plane of the cat's silhouette.
  - The silhouette is ~0.2 m above the ground, so the ground scale is larger by Hc/(Hc - h), about +1-2% for a camera 10-20 m up.
  - That gives about 1.16-1.17, consistent with route 1.

## Answer
- 1953 = 1.17 m. 1957 = 1.17 m (same scene, same camera, same marks).
- Confidence: medium.
  - The measurement itself is tight (~1%).
  - The main risk is interpretation: the wall is invisible in the segmented clip, and the label could be the stone width without the joint gap (~1-2% smaller).
- The current answers 1.9 and 1.5 disagree with each other and with this pitch. Both look wrong: the scene and camera are the same, so the values must be identical.

Scripts are in scripts/. The PNG crops are the small images I viewed.
