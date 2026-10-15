# simulation_0268 (A2SC, 24 fps, 2560x1440, 72 frames)
Scene: white spacecraft (top/bottom view) translating right->left over a static sky background, uniformly accelerating from rest at frame 0.
Prior: acceleration at 1.0 s = 4 m/s^2.

Method
- Background = last frame (ship gone). Dark fins (value<90) tracked as connected components with darkness-weighted sub-pixel centroids:
  front fin pair, outer rear fin pair, inner rear fin pair (track.py, dark.py, fit.py, fit2.py).
- Each track fits a quadratic with residual 0.1-0.25 px; the motion starts at frame 0.00 (vertex). Constant pixel accelerations:
  front 1.239, rear-outer 1.211, rear-inner 1.184 px/frame^2. The differing values come from mild perspective parallax: the parts sit at slightly different depths (~5%).
- Speeds use ratios only, so they do not depend on scale: v = v_px/a_px * 4 m/s^2 / 24, with backward difference p(i-1)-p(i) taken from the fit.
  All three tracks agree: 1.916-1.921 m/s at frame 12 and 3.916-3.921 m/s at frame 24. The instantaneous a*t values would be 2.0 and 4.0.
- Scale: k = 4/(576*a_px) m/px for each depth; rear-outer (mid body) gives 0.005736 m/px.
  Length: about 1040 px nose to tail when the ship is centred in the frame (frames 37-38), giving 5.97 m. A per-feature depth-scaled computation at frames 18 and 48 gives 5.93-6.00 m.
  Width: vertical extent of the rear fins is about 511 px (y 463-976), giving 2.93 m.

Confidence: speeds high (+-3%); length medium-high (+-3%); width medium (+-4%, depends on whether the bbox includes the fins; it should).
