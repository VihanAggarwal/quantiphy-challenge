# Lab audit, family 0015 (captured_0015 / 0015s / 0015x; one event, one label set)

## Scene
- 73 frames at 24 fps, 1280x720. One woman (grey t-shirt, navy parachute pants, Samba shoes) stands still at about
  x 290-470 px and tosses a brown plush toy twice. The toy is the Tanooki-Mario plush: brown suit, white gloves, striped
  tail, the same prop as the 0062 "mario toy".
- No depth_info. The only prior is g = 9.8.
- Toss 1: the toy leaves the hands at video frame ~14, apex at frame 18.85, caught at frame 23.
- Toss 2: release at ~52, apex at 54.7, caught at 59. The toy is then lowered to the hip by frame 66.
- The camera pose is identical to captured_0041 and 0047. Phase correlation of the backgrounds gives a 0.5 px shift
  (`pose.py`, `xref/blend_0041.jpg`).
- Clock: there is a 25 fps capture with one frame dropped before video frames 12, 36 and 60, the same pattern as the other
  lab audits. The toy step from 59 to 60 is about 70 px against about 30 px for its neighbours.
  - Video frame 14 = capture frame 15 = t 0.60 s.
  - Video frame 62 = capture frame 65 = t 2.60 s.
  - The 24 fps mapping (frames 14.4 and 62.4) gives the same frames.

Constants: f = 711, principal point (640, 360). Within a flight there is no drop, so the time per frame is 1/25 s.

## Scale from gravity (route 1, this clip)
- The x render is a matte on white. The toy separates as its own component in frames 17-22 and 53-58 (`gfit.py`).
- Quadratic fits of the vertical position give these pixel accelerations:
  - centroid: 4.67-5.28 px/frame^2;
  - toy top (most stable feature, rms 0.11 px): 5.14-5.57;
  - toy bottom: 4.57-5.43.
- I take a = 5.1 ± 0.4 px/frame^2, which is 3190 px/s^2 at 25 fps.
- This gives a scale of 0.307 cm/px at the toy (range 0.285-0.335) and a toy depth z of about 2.18 m (2.03-2.38).
- The horizontal acceleration is about 0, so the toy goes mostly straight up.

## Rows

| qid | render | question | current | measurement | verdict |
|---|---|---|---|---|---|
| 2266/2271/2276 | o/s/x | person height | 164 / 160 / 165 | matte 133-642 = 509 px. Route 1 (gravity): 156 cm if the person is at the toy depth; 165-172 cm if the body is 0.1-0.2 m behind the toy (the toy is in front of her). Route 2 (identity transfer): the same woman is the left person in 0018, where the 0018 audit measured 162-167 cm with stated range 3.13 m. Route 3 (floor, from the 0041 ball on the floor with the same camera pose): 162 cm (level camera) to 176 cm (pitch -5 deg); this route is sensitive to pitch. | OK |
| 2267/2272/2277 | o/s/x | toy v at 0.6 s | 150 / 170 / 190 | Forward difference between video frames 14 and 15 is 20-23 px, which is 154-177 cm/s at 0.307 cm/px. Physics only (scale-free): g x (apex - t) = 9.8 x 4.35/25 = 170 cm/s. | OK (motion row, not >1.5x) |
| 2268/2273/2278 | o/s/x | toy height | 28 / 32.09 / 28.72 | In-flight bbox height 91-98 px x 0.307 = 28.6 cm (26-33 over the scale range). Cross-check in 0062: the same toy lies on the floor at stated range 2.016 m, about 113 px long in the image at about 0.266 cm/px, so 30 cm or more (it is foreshortened on the floor). | OK (all within about 12%) |
| 2269/2274/2279 | o/s/x | shoulder breadth | 34.5 / 36.75 / 32.02 | The outer sleeve edge to edge is about 95 px (x 296-392, frame 0), which is about 30.6 cm apparent at z 2.29. The body is turned about 30-45 deg to camera right, so the clicked 3D breadth is likely 32-40 cm. | OK (no route gives a ≥15% difference) |
| 2270/2275/2280 | o/s/x | toy v at 2.6 s | 130 / 172.4 / 146.6 | After the second catch the toy is lowered (`toymask.py`, `g_x58_69.jpg`). Its centre y is 61: 275, 62: 305, 63: 325, 64: 342, 65: ~348, 66: 355. The forward difference 62->63 is 16-20 px, which is 123-154 cm/s (114-168 over the scale range). If the label were taken one frame later (63->64, 17 px), it would be about 130. | OK (not >1.5x off; motion row left alone) |

## Result
No fixes for family 0015. 15 rows checked, all kept.
- The person and toy sizes agree with two independent scales: in-clip gravity, and transfer of the same person and prop
  from 0018 and 0062.
- The two velocity rows agree with the gravity-scaled tracks on the established 25 fps drop-frame clock.

Scripts: `extract.py`, `crops.py`, `gridcrop.py`, `matte.py`, `track.py`, `gfit.py`, `toymask.py`, `pose.py`, `b41.py`,
`b41b.py`, `vlines.py`, `xref.py`.
Images: `montage_{o,s,x}.jpg`, `crops_o_*.jpg`, `g_*.jpg`, `toymask_58_69.jpg`, `xref/*.jpg`.
(The full-frame PNG dump was deleted because the disk is nearly full: 469 MB free.)
