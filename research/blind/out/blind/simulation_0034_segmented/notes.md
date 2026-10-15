# simulation_0034_segmented: notes

Video: 1080x1080, 72 frames, 24 fps, static camera, white background (segmented). The objects are a walking person on a sandbar (left), an eagle flying away (top centre) and a red fishing boat seen bow-on and approaching the camera (right).

## Scale (focal length)
- The prior is a person height of 1.75 m. In frames 0-1 the person is standing. Head top (sub-pixel) is at y=456.5 and shoe bottom at about 526.5 (above the white segmentation halo), so h is about 70.0 px. In walking frames h is about 66.5-67 px because of the gait pose.
- Person range is 92.19 m. The ray is about 5.5 deg off-axis, so depth is 91.76 m.
- f = 70*91.76/1.75 = 3670 px (standing). Using walking frames instead would give about 3500.
- Chosen f = 3650 px, leaning to the standing value. That is a horizontal FOV of about 16.8 deg.

## Boat (qid 1828-1830)
- Image height (mast top to keel) grows 323 -> 365 px over the clip. A 1/h fit with the range anchors (96.90 at t=1, 92.85 at t=2) gives a constant radial speed of 4.056 m/s (fit residual 1 px).
- The focus of expansion sits on the boat (x about 922), so the boat moves along the line of sight and the lateral speed is negligible. Speed = 4.05 m/s. Confidence: high.
- Height: h_px*R = 32370 px*m at d=0. A fit of the depth offset of the silhouette features gave d = 0 +- 2 m. H = 32370*0.994/3650, about 8.8 m including the mast; the faint mast tip adds about 0.5%. Confidence: medium, since it scales with f.
- Width: hull beam is 112.9 px at t=1. The widest hull section is fitted at 2.4 m nearer than the origin, giving 2.91 m (2.98 m at d=0). A black davit arm on the port side sticks out to x=852 px, which makes the full extent about 126.5 px, or 3.31 m. The answer of 3.2 m is a hedge between the hull beam and the full AABB. Confidence: medium-low.

## Person speed (qid 1831)
- Head-x and centroid-x tracks over 71 frames, with range 92.19 m (nearly constant) and 3D built from (u, v, R).
- Net path speed is 1.20 m/s. The smoothed per-frame mean is 1.216 m/s. From t=1 to t=2 it is 1.195-1.21 m/s.
- Answer 1.21 m/s. Confidence: medium (scales with f).

## Eagle (qid 1832-1833)
- 3D positions from the centroid at t=1 and t=2 (same flap phase, period about 24 frames) and the ranges 91.69 and 103.43. Velocity is (1.25, -0.62, 11.74) m/s, so speed = 11.83 m/s. The image track over the whole clip fits constant velocity. Confidence: high (mostly radial, so almost independent of f).
- Wingspan: per-frame sub-pixel horizontal extent times the extrapolated depth over f. The maximum in each flap cycle (flat wings) is 1.667 (frame 4), 1.660 (frame 32) and 1.701 m (frame 54). Answer 1.70 m. Confidence: medium.
