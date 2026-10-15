# simulation_0287 — plane fly-by (2D sim, static camera, 2560x1440, 72 frames @25 fps)
Prior: plane speed 22.16 m/s = 0.8864 m/frame. Plane flies right->left at constant image-height (y extent 316-527 constant -> constant depth, path parallel to image plane).
Strong perspective: features move at different px speeds by depth (template tracking, px/frame):
canopy ~45.8, nose 43.7, near tail fin top 42.6, exhaust 42.15, gear 41.27, far pods 39.1. Twin tail fins: near/far parallax ratio 1.064 -> mid-plane ~41.3 px/frame (= gear).
Each feature: k_i = v/s_i (m/px at its depth); world X_i = v((x_i-c)/s_i + t) with c=1280.

- 1006 length: X-extent between extreme features (nose track vs tail tracks), perspective-invariant: 14.4-14.6 m (c varied +-180 px). Planar check: min bbox ~676 px * 0.02146 = 14.5. -> 14.5 m (conf high).
- 1007 height: horizon row y_h ~760 from vanishing line of twin tail-fin tops (frames 56, 64). Y = (y_h - y)*k. Top = near tail fin top y=313 (k=0.02081) -> 9.30 m; bottom = far pod rear y=528 (k=0.02267) -> 5.26 m. H ~4.04 (3.94-4.1 over y_h 720-800). Naive planar 215 px*0.02146=4.6 (overestimates due to near/far parallax). -> 4.1 m (conf medium).
- 1008 displacement 0.5-1.0 s: speed constant (linear tracks, residual <0.1 px) -> 22.16*0.5 = 11.08 m (conf high).
