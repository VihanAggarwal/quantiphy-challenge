# internet_0037 - overhead drone view of a swimmer, near-static camera (drift ~10 px over the clip, corrected)
- Scale: the swimmer's head-to-toe length in 4 frames (0, 30, 90, 125) = 650/713/620/710 px, median ~670 px = 1.63 m -> 0.00243 m/px (moderate confidence, +/-8%).
- Track: centroid of a skin-colour mask (track.py -> track.txt), with local linear fits around frames 0, 49.7 and 124.8; camera drift removed with phase correlation on the deck (cam.py).
- Distances: 0-2.07 s: 356 px -> 0.42 m/s; 2.07-5.20 s: 563 px -> 0.44 m/s; 0-5.20 s: 917 px -> 0.43 m/s. A head-tip check gives about 185 px/s, which agrees.
- Acceleration: nearly constant speed; (0.437-0.418)/2.6 s is about 0.007 -> 0.008 m/s^2 (low confidence; a quadratic fit gives a small deceleration instead).
- Pool width: water from y~178 (top coping) to y~2056 (bottom coping) = 1880 px -> 4.57 m (medium confidence; a shallow ledge at the top edge makes the boundary ambiguous).
