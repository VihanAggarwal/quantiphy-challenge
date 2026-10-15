# captured_0041x (lab, segmented, 1280x720, 49 frames at 24 fps)

Scene: a person on a green background kicks a soccer ball toward the camera. The ball rests at pixel (572,530), about 39.75 px across, from frame 0 to 32. The kick lands at frames 33-34. Afterwards the ball is motion-blurred.
Ball track (blob centroid, chord across the motion through the centroid):
f35 (579,565) ~48 px; f36 (584.5,614.1) 55.2 px; f37 (590.2,637.4) 60 px; f38 (595.3,661.4) 68.5 px; f39 (603.5,685.3) ~76 px (cut by the frame edge).
The image step from f35 to f36 is twice the normal step, which suggests a dropped frame (a 25 to 24 fps conversion). t=1.5 maps to f36 and t=1.6 maps to f38 (~38.4).
Check: 2.544*55.2/68.5 = 2.05, close to the label 2.074. The forward-difference speed from f36 to f37 is about 5.17 m/s at 25 fps, which matches the 5.21 prior.

Pinhole model: f=711, principal point (640,360), depth treated as planar Z.

- 2915 diameter: 55.2 px * 2.544 m / 711 = 19.7 cm. Adding the front-surface ToF offset gives about 20.5 cm. From f38: 68.5*2.074/711 = 20.0 cm, or 21 cm with the offset. A physical ball would be size 4 (20.5 cm) or size 5 (22 cm). Answer 21 cm, which is within 5% of both. Confidence medium.
- 2916 displacement: P(1.5)=(-0.199,0.909,2.544) and P(1.6)=(-0.130,0.881,2.074) give 0.476 m. With depth taken as range instead of planar Z it is 0.49. Answer 0.48 m. Confidence fairly high.
- 2917 ball-person distance: the person's depth is not given. Estimated route:
  - Rest-ball size ratio: 55.2/39.75 = 1.39, so the rest ball is at about 3.53-3.67 m.
  - Ground rows with a level camera: rest ball at 3.68-3.81 m.
  - The person's standing foot at 1.5 s is about 3% closer than the rest ball. The ToF surface of the torso is about 0.1 m in front of the body centre. So the person's depth is about 3.5-3.6 m.
  - Assumed click point: torso/hip (640, ~345).
  - 3D distance is 1.33-1.48 m. Answer 1.40 m. Confidence low-medium, because the person's depth and click height are both uncertain.
