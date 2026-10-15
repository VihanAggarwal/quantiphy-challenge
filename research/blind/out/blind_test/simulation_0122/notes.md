# simulation_0122 — sword length (qid 264), prior g = 9.8 m/s^2

Scene: static camera, portrait 1152x2048, 25 fps, 40 frames. A vertical sword drops from the top of frame
(released ~1 frame before frame 0, from rest) and sticks into a rock at frame 17 (x ~ 576, centre column).

Tracking: background = median of frames 20-39 (y<740) / frames 0-7 (y>=740); template matching (NCC, sub-pixel
parabola peak) on |frame - bg| images with templates of tip, crossguard and pommel cut from frame 13.
- tip y (f0..16): 55.6 65.5 83.1 107.2 139.4 176.5 220.8 271.4 333.0 399.6 471.7 551.5 638.3 731.0 830.4 935.4 1048.3
- pommel top y (f10..16): 52.9 132.9 219.4 313.0 413.5 521.0 635.5  (parabola rms 0.07 px, a = 6.94 px/frame^2)
- guard y (f9..16): 51.0 123.8 203.9 290.7 384.0 484.3 591.7 706.0 (a = 6.86 px/frame^2)
- tip f8-16 a = 6.57 px/frame^2 -> image scale shrinks slightly downward (camera pitched down); apparent
  pommel-tip length shrinks 418.8 -> 412.7 px from f10 to f16.

Model: all three features move along the same 3D vertical line, so image y = 1D homography of the drop distance
d = 0.5*g*((t-t0)/25)^2; feature offsets (blade-to-guard Lg, total length Lp) fitted jointly (6 params, LM).
- all points: Lp = 0.944 m (rms 0.69 px); excluding noisy tip f7,f16: 0.946; tip>=8 only: 0.946; linear-scale
  (C=0) variant: 0.947-0.956. t0 ~ -1.0 frame in all fits (consistent release from rest).
- Frame-13 pommel top edge read as ~314 vs template ref 313 -> -1 px (~-0.002 m). Final 0.944 m.
- Simple check: pommel a = 6.94 px/fr^2 -> 2.26 mm/px x 418 px = 0.945 m.

Answer: 264 -> 0.944 m (sword pommel-to-tip, = vertical AABB dimension). Confidence: high (~3%), residual risks:
rigid-body damping (would make true value ~1-2% smaller) or a 24-fps render timebase (would make it ~8% larger).
