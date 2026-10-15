# simulation_0184 - tool box falls onto a ramp, then slides down it (1920x1080, 24 fps, 45 frames)

## Camera / scene geometry
- Static camera. The background is the median of all frames. Box masks come from background difference and look clean in the overlays.
- Vanishing points from brick mortar lines:
  - Back wall: VP1 = (-5160, 542.5).
  - Side wall, perpendicular to the back wall: VP2 = (1690, 542.2). A floor-plank seam gives VP2 at about 1705.
  - Both lie on the horizon y = 542, so the camera is level.
- f = sqrt((cx-u1)(u2-cx)) = 2110-2125 px (HFOV about 49 deg). I used f = 2115.
- The ramp runs along the back wall (VP1 direction) and slopes about 28.5 deg. The box track and the ramp edges point to the same vanishing point.
- depth_info is taken as the range to the box centre. Check: with the centre held in the plane parallel to the back wall, the range at t=0.5 s comes out as 9.088-9.096 m (given: 9.096). The optical-axis Z convention fits less well.

## Motion
- Body-point tracks: the red LED on the lid (colour centroid) and an affine ECC template track (frame-30 template). The two agree within 0.2%.
- 3D model: the box moves in the vertical plane parallel to the back wall that passes through the centre. Rays are intersected with that plane, so positions are known up to one scale k.
- Free fall (frames 0-7): the box starts from rest at frame 0. Pixel acceleration is 4.17 px/frame^2 (4.10-4.21 across templates).
- Sliding (frames 22-42): quadratic fit, constant acceleration with residual about 0.1 px. In k-units, a = 0.2107; backward-difference speeds are v(1.0) = 0.2510 and v(1.5) = 0.3564. Assuming the motion runs exactly along the ramp-edge direction changes these by less than 0.3%.
- Scale k:
  - Prior (ramp acceleration 1.58 at 1.25 s): k = 7.50.
  - Gravity (g = 9.81 with Blender's 0.04 linear damping, effective 9.75): k = 7.57.
  - These agree within 1%, so the scene units are consistent with g = 9.81. I used k of about 7.53-7.55.
- a(0.2 s) = 9.67-9.75. The physics expectation is 9.81 - 0.04*v, about 9.73. Answer: **9.73 m/s^2**.
- v(1.0 s) = 1.88-1.90. Answer: **1.89 m/s**.
- v(1.5 s) = 2.67-2.69. Answer: **2.68 m/s**.

## Size
- Fitted a cuboid aligned with the room axes, plus yaw and roll, to the silhouettes of frames 0, 4, 22-42 (Nelder-Mead on IoU, several restarts).
  - Scale: range 9.194 m to the box centre at frame 0.
  - The centre stays in the plane parallel to the back wall.
- Results at f = 2115: L = 1.205-1.222 m, H = 0.684-0.718 m. This holds with or without forcing the visible front-right edge to sit at u = 656 px.
- How the results move with f: at f = 2050, L = 1.245 and H = 0.72-0.73. At f = 2160, L = 1.17-1.19 and H = 0.68-0.69.
- Corner-based check at frame 0: the front-right vertical edge spans y 242 to 420 px (178 px). This gives H = 0.706 m.
- Motion-based scale is about 1-2% smaller than the range-based scale. The rounded cuboid is about 1% bigger than its IoU fit. These roughly cancel.
- Length: **1.21 m**. Height: **0.70 m**.

## Confidence
- 1429 a(0.2 s): high (prior route and gravity route agree).
- 1430 / 1431 speeds: high (the speed-to-acceleration ratio does not depend on scale; the prior sets the scale).
- 1432 length: medium (depends on f within ±2% and on the cuboid model).
- 1433 height: medium (spread ±3%).
