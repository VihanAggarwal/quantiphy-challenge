# simulation_0019: method notes

Video: 1080x1080 at 33 fps, 97 frames. The frames are rotated 90 deg, so I rotated them clockwise to get an upright view.
Static camera. Vertical edges stay vertical and facade edges stay horizontal, so the camera has no pitch or roll.
The floor-seam vanishing point is at about (539.5, 539.0), so the horizon is y~539.25 and the principal point is the image centre.

## Calibration
- Person (prior 1.87 m). Feet: the far foot plants at y=781 and the near foot at y=786.5, so the ground under the pelvis is at y~783.7. These values do not change between t=0 and t=1, so the depth Z is constant and the person walks parallel to the image plane. This means the depth values (6.84 to 6.49) are Euclidean range, not optical-axis Z.
- Head top at peak height is y~520.8, so the person is 262.9 px tall. That gives s = 0.00711 m/px at the person's depth.
  An independent route from D0^2 - D1^2 = s^2[(x0-cx)^2-(x1-cx)^2] gives s = 0.0071 to 0.0072. Camera height H = s*244.45, about 1.74 m.
- f*H: if the person's distance were to the pelvis, f*H would be about 1549 (f~891). In that case the nearest visible display panel (the right one) would be at 11.35 m or more, against the stated 11.042 m.
  If the reference point is at floor level, f*H is about 1502 (f~864). Then the right panel's bottom centre is at 11.02 m (stated 11.042) and the sculpture origin sits at about 0.6-0.67 m, the top of the dark box and bottom of the stone base. Both checks fit, so I adopted the floor-level reference.
  The sizes depend on H, and the f-dependent terms are small.

## Measurements (background median image)
- Dark box: front face x 331.0 to 632.3, bottom y=894.5, top-front edge y~773. Width 1.47 m, height 0.60 m.
- Light stone base (tapered square slab on the box): bottom-front edge y~767, width 258.5 px, which is 1.30 m. Top-front edge y~703.5. Fitting a frustum gives a top side of 1.16 m and a height of 0.306 m (top at 0.904 m).
- Sculpture tip at y=389.5, assumed at the pedestal centre depth. Top is at 2.60 m, so the sculpture alone is 2.60 - 0.904 = 1.70 m tall (2.00 m if the stone slab is counted as part of it).
- Pedestal identity: the "pedestal" and the "sculpture" have identical origin distances (5.085 m), so they share one origin, located at about the stone-base bottom. That points to the stone base being part of the sculpture asset, with the dark box as a separate gallery plinth.
  I answered for the stone base (P~0.6) but hedged the width toward the dark box value (1.47 m).
- Nearest panel (right one, rotated ~28 deg): lower-tier base front edge from (655.5, 676.1) to (781, 686.0), end face out to x=784.5 (depth ~0.19 m).
  World AABB X-extent is 1.48 m; local length is 1.56-1.57 m. Top bar at y~517.3, so the height is 2.01 m.
- Speed: head and torso tracking gives 5.567 px/frame (linear fit over frames 0-96; stride from foot plants 189.6 px per ~34 frames).
  v = 5.567*33*0.00712 = 1.31 m/s. Around t=0.5 s the upper body runs about 4% below the mean (gait phase), so I answered 1.30.

## Answers / confidence
- 1090 speed 1.30 m/s (medium-high)
- 1091 pedestal width 1.34 m. Stone base is 1.30 and the dark box is 1.47; hedged (medium).
- 1092 pedestal height 0.31 m. Stone base is 0.31; the dark box would be 0.60 (low-medium, depends on which object is meant).
- 1093 sculpture height 1.73 m. Measured 1.70; it would be 2.00 if the stone slab is included (medium).
- 1094 panel width 1.52 m. AABB is 1.48 and local length is 1.56 (medium).
- 1095 panel height 2.01 m (medium-high).
