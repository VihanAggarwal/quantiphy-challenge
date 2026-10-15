# simulation_0015 – notes

Scene: a static camera looking into a gallery atrium. A human (1.87 m) walks toward the camera.

## Camera
- Vertical lines are vertical (dx/dy about 0), so the camera is level with no pitch or roll.
- Floor-seam vanishing point is at (539.7, 539.2), so the horizon is y0 = 539.2.
- Human ratio (f-free): Hc = 1.87*(y_feetmid-y0)/(y_feetmid-y_head). Frames 0, 33 and 99 give 1.385, 1.413 and 1.397.
- depth_info behaves like optical-axis Z, not range:
  - The display panel at 11.874 sits about 6 m off-axis. Under the Euclidean convention it would need its base near y=656, but it is observed at y≈643.
  - The pedestal and the sculpture have identical depths.
- K = f*Hc ≈ 1230 from:
  - human t0/t1: 1232 and 1245
  - pedestal: 1210
  - panel: about 1233
- f ≈ 885 px from the human's pixel height with Z: 890 and 881. Hc ≈ 1.39 m.

## Measurements (zoomed crops plus LSD lines)
- **Pedestal lower block:** x 465–614.5, y 614.5–678. Width 1.49 m, height 0.63 m.
- **Tapered cream plinth on the block:** top y=579.5, which is 0.98 m above the floor.
- **Sculpture tip:** y=423.7, which is 2.64 m above the floor.
- **Q1073 and Q1075 are ambiguous:** the plinth could belong to the sculpture asset or to the pedestal.
  - Sculpture height is 2.01 m (plinth in the sculpture) or 1.65 m (plinth in the pedestal). Answered 1.93, hedged towards 2.01.
  - Pedestal height is 0.63 m (block only) or 0.98 m. Answered 0.65.
- **Panel:** top rail at y=490.5, base on the floor, frame plane at Z=11.874. Height 2.04 m.
- **Benches:** two mirrored Z-base benches aligned with X/Z. The foot near face bottom is at y=680.5 (Z=8.73).
  - Seat near face is 78 px wide, so width 0.77 m.
  - Far end is at Z≈10.9, so length about 2.2 m.
  - Cushion top is at y≈628.5, so height 0.51 m (whole bench, floor to seat top).
- **Roof:** back wall meets the floor at y=574.0, so Z_wall = 35.4 m.
  - The back roof band runs from y 191.7 to 209. Its bottom is at 14.6 m and its top at 15.3 m. Clear height answered as 14.9 (hedged).
  - The band is 0.69 m tall. Lattice beam section analysis gives about 0.45–0.7 m. Thickness answered as 0.6.
- **Speed:** depths are 12.26 at t=0 and 10.97 at t=1, so Δ ≈ 1.29–1.30 m/s. Lateral drift is negligible. Answered 1.30 (gait-phase variation unresolved).

## Confidence
| Question | Confidence |
|---|---|
| 1074 pedestal width, 1076 panel height | high (±3%) |
| 1078 bench width, 1079 bench length | medium |
| 1077 bench height | medium (if "seat" means only the slab: about 0.16) |
| 1073 sculpture height, 1075 pedestal height | medium-low (object-boundary ambiguity) |
| 1080 roof clear height | medium |
| 1081 roof thickness | low |
| 1082 speed | medium-high |
