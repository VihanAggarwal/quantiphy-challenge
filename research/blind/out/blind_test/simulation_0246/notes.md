# simulation_0246 (V2MS, top-down 2D view, antelope + rabbit walking right)
Scale: antelope template-matched (torso+head template from f30) across all 75 frames: 721.6 px in 74 frames = 9.75 px/frame = 292.6 px/s
(gait oscillation 7.4-11.7 px/f; used mean). Prior 1.277 m/s -> 0.004364 m/px.
- 831 antelope length: tail tip to nose measured on zoom tiles at f0,12,24,36,48,60,74: 605,660,636,663,698,669,715 px (tail swings);
  median ~665 px -> 2.90 m. Confidence: medium (pose-dependent tail, unknown frame of AABB).
- 832 rabbit speed at 1s: rabbit centroid track (orange mask); hopping; smoothed backward diff at f30 ~9.3-11 px/f, used 9.6 px/f -> 1.26 m/s. Confidence: medium.
- 833 rabbit length: orange body + pale head extent on zoom tiles at 8 frames: 88-98 px, median ~91 px -> 0.40 m. Confidence: medium-high.
Scripts in s/.
