# simulation_0269 (A2SS, top-down view of phoenix flying left, 24 fps, 72 frames, 2560x1440)
Method: saturated-colour mask per frame (shadow is grey, excluded). Beak (leftmost mask x) track fitted with
quadratic + 25-frame flap harmonics (rms 0.86 px). Motion = constant acceleration from rest at frame 0:
a = 0.4137 px/frame^2 = 238.3 px/s^2 (deg 3/4 fits identical; tail-tip track gives same a).
Scale: 2 m/s^2 / 238.3 px/s^2 = 0.00839 m/px. Bird pixel length constant over video (no depth change).
- 949 body length: beak tip ~1483 to tail-rod tip ~1935 at f0 (~447 px; masks 427-442) -> 3.75 m (medium conf.; AABB/rest-pose ambiguity)
- 950 wingspan: max y extent with wings spread (f21/46/71) ~625-629 px -> 5.28 m (medium; rest pose may differ)
- 951 speed 0.5 s: v=2t -> backward diff 0.958, continuous 1.0; hedged 0.98 (high)
- 952 speed 1.0 s: backward diff 1.958, continuous 2.0; hedged 1.98 (high)
