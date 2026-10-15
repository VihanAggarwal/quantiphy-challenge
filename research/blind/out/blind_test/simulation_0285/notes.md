# simulation_0285 — plane flying right-to-left, static camera, 2560x1440, 72 frames, t = frame/25

Method
- Background = median over frames; plane mask by |frame-bg|>25; per-frame bbox; small-patch frame-to-frame template tracking.
- Motion is parallel to the image plane: every tracked point has a constant px speed (quadratic terms ~0), but speeds differ by depth:
  near canted fin 46.35, nose 43.76, mid fuselage 43.8, tail extreme 41.49, far wheel 41.3, lowest far element ~39.5 px/frame.
  Each point's metres-per-pixel = v/(25*s) = 0.8864/s (v = 22.16 m/s, pure translation).
- Ground shadow row-speeds: y = 420 + 11.58*speed -> horizon y_h ~ 420 (plane flies on horizon, camera pitched down ~10 deg,
  f*tan(theta) = 300 px; f ~ 1700 from shadow wingspan plausibility, only enters via cos(theta)).
- Length (camera X = world horizontal flight axis): X = (x-1280)*0.8864/s per extreme point -> nose to tail 14.45 m, constant over frames.
- Height: world height = 0.8864*cos(theta)*(y_h - y)/s. Top = rear fin tip (y~312, s 42.47) -> +2.54*k; bottom = far low element
  (y 526, s 39.5) -> -2.68*k; H = 0.8864*0.985*5.23 = 4.56 m (naive single-scale 219 px * 0.0203 = 4.45).
- Displacement 0.5-1.0 s: constant velocity -> 22.16*0.5 = 11.08 m.

Confidence: length high-medium (14.45, range 14.4-14.8); height medium (4.45-4.6); displacement high.
