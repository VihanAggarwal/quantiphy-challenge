# simulation_0173 - notes

Scene: static camera, 1920x1080, 24 fps, 40 frames. A white regional jet with its gear down flies right to left, side-on,
above a sea-stack island (a rock cliff with trees on a sand beach). Prior: airplane speed 153.582 m/s, which is 6.3993 m/frame.

## Scale from the prior
- I tracked the nose-wheel blob, the main-gear blob and the leftmost (nose) column against the median background, frames 8-31.
  The plane moves at a constant -61.37 px/frame (cross-correlation gives 61.35). Image y stays constant, the apparent size
  stays constant and the speed has no trend, so the motion is parallel to the image plane.
- Scale s = 6.3993 / 61.37 = 0.10427 m/px.

## Camera geometry check
- The two main-gear legs sit apart along the aircraft's lateral axis, so their image offset points toward that axis's
  vanishing point. Frames 10 and 30 (offset of +/-14 px in x, 8-9 px in y) put the vanishing point at about (968, 547).
  This means the camera is close to level and the true horizon is near y=547. The visible sea edge at y=893 is not the
  true horizon (the ocean plane is probably finite).
- Independent check: the vertical span of the wing in the plane's shadow on the sea is about the same as on the plane itself.
  That only works if the horizon is near y=550. If it were at y=893, the shadow's wings would look almost flat.
- The shadow moves at about 56.0 px/frame at row about 970, so the shadow is at 0.1143 m/px. Ground plane with y_h=547 gives
  a camera height of about 48 m. That puts the cliff base (rows 1005-1025) at Z/f = 0.103-0.104 m/px, the same depth as the
  plane, which fits the 2D planar design.

## Answers
- Q417, plane length: horizontal extent about 453 px (per-frame masks 450-458, shortest when the tail is near the vanishing
  point; aligned-median silhouette 455-458). 453 x 0.10427 = 47.2 m. Confidence: high.
- Q418, cliff height: the rock alone spans rows 625 to 1025, 400 px, which is 41.7 m with the 2D scale and 40.4 m by the
  ground-plane route. With the trees on top included (top at row 522) it is 503 px, 51-52 m. I can't tell whether the trees
  count toward the object's bounding box, so I hedged at 44 m, leaning toward rock only (the rock may also extend below the
  sand). Confidence: medium.
- Q419, main (rear) wheel diameter: the near main wheel's vertical extent at half level is 12.5 px (median over 11 frames)
  and its horizontal extent is about 13 px. Removing the tread-width perspective term (0.5-1 px) leaves about 12 px.
  12 x 0.10427 = 1.25 m. As a check, wheel/length = 2.65%, which is typical for a regional jet. Confidence: medium-high.
