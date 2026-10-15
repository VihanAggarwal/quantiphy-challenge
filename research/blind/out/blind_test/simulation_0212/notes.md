# simulation_0212 - method notes

Scene: static level camera, room with back wall + right wall, bench (with lamp, vase) and a leaning floor mirror against the back wall.
Black cat walks right/away, dog walks left/toward camera; both move parallel to the back wall (D1 direction).

## Camera
- Principal point (960,540). Back-wall floor line y=909.008-0.075024x, right-wall floor line y=563.304+0.128910x (rms 0.1 px), corner (1695,782).
- Horizon from carpet-stripe vanishing point (local FFT orientations, robust LS): (987,537.6) +-0.7; lamp column axis vertical to 0.03 deg -> roll ~0, pitch ~0.06 deg.
- f from orthogonal wall VPs + horizon: 2125-2151 px; f from cat speed prior (0.94 m/s, ranges 4.199/4.481, straight track): 2092-2110 px. Used f=2130.
- depth_info = Euclidean range (cat paw-row change 37 px between t=0 and 1 s matches range convention, Z convention predicts 26 px).
- Camera height h=0.784 m from closest bench leg foot (1405,840) at 5.69 m; consistent with cat ground contact (origin height ~0.01 m) and mirror AABB-bottom-centre range (6.414 vs 6.407).

## Measurements
- Cat: straight-line constant-velocity track (verified: predicted u(2s)=1228 vs observed 1231). r(0.5)=4.317, r(1.5)=4.685.
  Length/height from silhouette on cat midline plane, frames 0-21: L median 0.674 (f0 0.673), H median 0.486 (f0 0.494, tail tip highest).
- Bench (parallel to back wall, a1=28.1 deg): front feet line c2=4.32, top back edge c2~4.66-4.70, top surface height 0.455; length (BL corner u=1287 to FR corner u=1667) 1.03-1.06.
- Lamp on bench: base bottom row 661, top 397.5 -> 0.70; shade top 397.5, bottom rim ~494.5 -> 0.255; bottom rim width 191.5 px at Z=5.74 -> 0.516.
- Vase: bottom 654.5, top 469 -> 0.525.
- Mirror: bottom edge c2~4.59 (rows 818/808), leans back 0.2 m; top at 1.445 m; width 0.62-0.64.
- Dog: walks along -D1 at c2~3.63 (near paws); flank template track -> speed ~0.94-0.98 (raw) / 1.02-1.06 (smoothstep/poly fit) at t=1; 0.87-0.96 at t=1.5 (decelerating to stop by t=2).
  NOTE: dog depth label t=0.5 (4.625) is inconsistent with visible body (body range ~4.93 at t=0.5; reaches 4.625 at t~1.0). t=0 label matches body. Used body motion.
  Dog length incl. tail varies 0.93-1.31 with tail/head pose (median ~1.11); height 0.565 (back) to 0.675 (tail raised).

## Confidence
- High: 1615, 1616 (cat distances).
- Medium: 1605, 1606, 1608, 1611, 1612, 1613, 1609, 1610 (f uncertainty ~2%, edge reads).
- Medium-low: 1607 (top depth assumption), 1614 (lean/plane), 1617, 1618 (dog origin anomaly), 1619, 1620 (pose-dependent).
