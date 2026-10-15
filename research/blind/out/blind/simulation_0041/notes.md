# simulation_0041 notes (S2MC, 1080x1080, 24 fps, 72 frames; frame 0 duplicates frame 1)

Scene: an oblique top-down telephoto view of a beach. A person walks toward the camera on the sand, and a fishing boat ("AH805") moves left along its own axis.
The camera is static. It is NOT orthographic. The verticals (mast and cabin edges) visibly change lean as the boat moves, so I used a full pinhole model instead of a single m/px scale.

## Camera calibration (measured from this video only)
- Vertical VP: a subpixel fit of the cabin aft-port vertical edge and the mast edge over all 72 frames gives V_n ~ (-95, +4540) px from the image centre (bootstrap +-100).
- Boat motion VP (FOE): KLT-tracked 73 boat points. The tracks are straight lines (rms 0.03 px). These routes all give D ~ 32-33k px along the track direction, i.e. a horizon ~8000 px above the boat:
  - robust line convergence: D = 32.2k (5-95%: 26.8k-36.6k)
  - projective deceleration under constant speed: D = 32k
  - consistency of mast length growth: 32k
  - bow-stern length shrink: ~39k
- f^2 = -FOE.V_n gives f ~ 5900-6200 px (FOV ~10 deg) and a pitch of 52-54 deg. Whether the 1.2 deg lean offset is camera roll (A) or boat trim (B) is unresolved, so I averaged both.
- Scale comes from the person. The head-top silhouette is at 1.75 m (head sphere r = 0.1 m). The ground point under the head is the intersection of the shadow axis with the body vertical; the mean extent is 36.1 px.
  - This gives camera height H ~ 146-151 m (+-3% from +-1 px).

## Answers (mean over the hypothesis grid D = 30k/33k/36k x roll A/B)
- Q11 length 9.95 m: stem head (parallax height ~2.1 m) to the stern extreme (~0.75 m) along the motion axis. Range 9.66-10.18. Medium confidence.
- Q12 width 3.35 m: twice the port half-breadth (red-hull top / gunwale at ~1.05 m) relative to the bow-stern centreline. Range 3.33-3.42.
  - The foredeck is symmetric under this centreline. The direct starboard-rail chord gives only ~2.6-2.9 m because the rail is inboard.
  - Medium-low confidence.
- Q13 boat speed 4.16 m/s: constant velocity; in the model the world speed is constant from start to end. Range 4.03-4.30. Medium confidence.
- Q14 person speed 1.44 m/s: mean head ground speed (1.34-1.53 across hypotheses), +1% for the gait phase at frame 24 (near heel strike). Medium confidence.

Main risk: the camera pitch. If the horizon were much farther (~60+ deg pitch), all values would shrink by ~25-30%. But the FOE convergence, the deceleration and the mast-length growth all reject that.
