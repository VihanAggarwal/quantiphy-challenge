# 0032 independent re-measure (qids 2541, 2547, 2553: white ping-pong ball velocity at t=1.5 s)

Scripts and crops: research/next/labaudit2/0032/remeasure_work/ (scripts/, frames/). I did not read any other 0032 notes.

## Event
- The a, s and x renders are the same capture (tracks agree to <1 px), so all three qids share one label.
- The tennis ball is released at video frame ~21. It hits the white ball at v30-31. The white ball is motion-blurred
  and faster (~9-10 px/frame) at v32-35. From v36 on it rolls at ~5.8 px/frame lateral and 1.5-2.4 px/frame down.
- Dropped frame: both balls show a double step between video 35 and 36 (tennis 31 px vs 15/17; white 13.6 vs 9/5.2).
  This fits c(j) = round(j*25/24) with zero offset, so v35 = cap 36 and v36 = cap 38. Capture 37 is not in the video.

## Geometry (f=711, principal point (640,360))
- Table edges from the x-render silhouette (subpixel). The side-edge vanishing point is (717.6, 349.4). With f=711 the
  table corners come out at 90.0 deg, so the horizon is at about v=349.5 (slope 0.004).
- Camera height above the table from the ToF anchors at v36: ping-pong 1.353 m -> h=17.76 cm; tennis 1.183 m -> 17.87 cm.
  These two agree. The table priors give 16.8 (W=60.3) and 18.2 (L=76.0). I used the ToF scale (that is the label scale).
- Cross-checks of the horizon: room wall/floor lines give ~344. The ball's size-vs-row regression gives 356-362, but its
  bootstrap spread is wide. The table aspect would force ~356 only if the table were exactly 60.3x76 (then the corners are 91 deg).

## White-ball speed, rolling phase (plane model, ball centre at h-2 cm, 4 centre estimators: circle fit a/x, blob a/x)
- Forward step cap38->39 (video 36->37) from a smooth fit: 58-68, centre about 63-64 cm/s. A linear fit over v36-40 gives 60-66.
  The window average v36-48 is about 65.
- Horizon sensitivity: v_h 344 / 349.5 / 356 -> about 59 / 63 / 67 cm/s.
- Label-style (surface point along the ray, ToF) differs from the physical value by <0.5%.
- Second route (ball size -> range, anchored at v36): the v36-48 average is about 68-70 cm/s, which agrees with the plane
  model within ~7%. Its per-frame shape is too noisy for an instantaneous value.
- The direction of motion is mostly toward the camera (Vz ~ -60, Vx ~ +19 cm/s), so ToF noise lies along the motion.
  A single-step label is therefore noisy (about +/-1 cm ToF gives +/-35 cm/s).
- Check on the tennis ball (same plane model): roughly constant ~90-100 cm/s, so the table is not sloped much.

## Frame convention (main uncertainty)
- If the label frame for t=1.5 s is round(37.5)=38, or video frame 36: the step is cap38->39 and the value is ~64 cm/s.
- If it is int(37.5)=37 (the dropped frame): the step cap37->38 is in the slide-to-roll deceleration. The average over
  cap36->38 is 88-98, which gives about 80-85 cm/s for cap37->38.
- Expected-score scan with p(k=38)~0.62 is flat over 64-68. Recommended value: **66 cm/s** for 2541, 2547 and 2553.
  Physical value at k=38 is ~64 cm/s.
