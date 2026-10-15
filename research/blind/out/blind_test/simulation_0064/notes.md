# simulation_0064: method notes

## Scene
The camera is static and elevated, looking down the main road toward an intersection. The video is 2160x1080 at 24 fps, 72 frames (3.0 s).
- White Chevrolet Express van: drives straight toward the camera and accelerates.
- Yellow taxi: turns and leaves to the image left.
- Cyclist: rides toward the camera at constant speed.
- Pedestrian: walks left along the far-left sidewalk. It is hidden behind the traffic light before frame ~31.

## Camera model (work/cam.py)
- Principal point is the image centre. Roll is ~0.
- The road-edge vanishing point is (1086, -122.5). The near and far road segments agree, and the van and bike focus of expansion matches it. This gives the horizon row, so pitch = atan(662.5/f).
- f, from several routes:
  - Vertical vanishing point from poles, traffic-light housings and building pillars: ~2130-2280.
  - Pedestrian lateral motion against its depth change (D 38.347 -> 38.722): ~2150.
  - Cross-street width equal to main-road width: ~2120.
  - Used f = 2150 px, HFOV ~53 deg (likely a 36 mm lens).
- Depth_info convention: range to the origin is consistent for the bike, taxi and pedestrian.
- Camera height above the road:
  - taxi at frame 38 (wheel contacts plus heading) gives 6.83 m;
  - pedestrian feet gives 6.77 m plus the sidewalk;
  - bike gives ~6.75 m;
  - used H = 6.85 m.
- The cyclist's head-top height stays at a constant 1.60 m over frames 36-54, which checks the model.
- Van anomaly: the van's depth_info (38.14 -> 34.05 m) cannot be reconciled with the visible van.
  - Its visible displacement between t = 0.58 and 1.58 is only ~2.9 m. That is less than the 4.09 m change in range, which violates the triangle inequality.
  - The van sits on the road next to the bike, its shadow is attached, and it moves along the road focus of expansion.
  - So van sizes come from the ground plane, not from its depth values.

## Answers
| qid | answer | how it was measured | confidence |
|---|---|---|---|
| 1306 taxi speed at 2.5 s | 4.23 m/s | Template-tracked wheel hubs over frames 50-71 give 12.33 px/frame at t ~ 2.48. Heading is parallel to X, so speed = px speed x Zc / f with Zc = 30.7 m. | medium-high |
| 1307 lane width | 4.0 m | Road is 12.04 m between curbs. There are no lane markings. Taxi and van lateral positions fit 3 lanes of 4.0 m; 2 lanes would give 6.0 m. | low |
| 1308 van height | 2.18 m | Roof-top silhouette over many frames plus the windshield top, assuming the van length is ~5.5 m. | low-medium |
| 1309 van width | 2.35 m | Body front face is 1.94 m; mirror to mirror is 2.42 m. Answer is weighted toward an AABB that includes the mirrors. | medium |
| 1310 taxi length | 5.05 m | 3D box fit to the silhouette extents over frames 38-70 (rms 4 px; 1-3 px for frames 50-70). The fit gives 5.00 m, raised slightly for rounded corners. | medium |
| 1311 taxi height | 1.64 m | Top of the roof sign at frame 68 in side view. A frame-0 front-view check gives ~1.6. | medium |
| 1312 taxi width | 1.93 m | Front view at frame 0: body ~1.86 m, including mirrors ~1.98 m. | medium |
| 1313 bicycle wheel diameter | 0.66 m | The wheel is not resolvable; it is seen end-on and blurred. Estimated from bike/rider proportions (head 1.60 m, hands ~0.85 m high, ~0.45 m apart). | low |
| 1314 traffic light height | 4.92 m | Base on the sidewalk up to the top of the sign on the signal head. Near-left gives 4.93, near-right 4.90. The housing top alone is ~4.25. | medium-low |
| 1315 pedestrian average speed | 1.22 m/s | Shirt-centroid track at a constant 2.99 px/frame with Zc = 36.26 from depth, giving 1.21. The depth-only route (dX between 0.58 s and 1.58 s) gives 1.20. Slightly raised for gait bob. | high |
| 1316 pedestrian height | 1.77 m | Head top at row ~192.5 and feet at row ~297, placed at the 3D position from the frame-38 depth. | medium |
| 1317 bicycle average speed | 5.43 m/s | Bike displacement between the depth samples is 5.43 m in 1 s (constant height of the origin). A scale-template track confirms constant speed across the clip. | high |
