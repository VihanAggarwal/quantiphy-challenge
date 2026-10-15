# internet_0029 - ball dropped onto desk (prior g = 9.8 m/s^2)

Video: 1080x1080, 25 frames @ 50 fps (0.5 s), static camera (door edge vertical -> ~zero pitch).

## Tracking
- Median-background subtraction, largest blob x<700, bbox-mid as centre (track2.py -> track.csv).
- Ball held still until ~frame 4 (bottom edge y~90), released ~t=0.06-0.07 s.
- Frame steps show DROPPED frames: double steps at 6->7, 11->12, 16->17, 21->22, 23->24
  => source was ~60 fps converted to 50 fps (1 of 6 frames dropped). Output frames n=10,15,20 map to
  source frames exactly 6 apart => t=0.2/0.3/0.4 s are real-time consistent.
- Parabola on 60-fps source indices fits to rms ~0.9 px (50-fps uniform time: rms ~12 px).
- Pixel acceleration declines over the fall (early ~9500, late ~8600 px/s^2); ball half-max width
  shrinks 77 -> 73.3 px => ball recedes from camera (~4%). Depth-aware model
  Y = D*(y-540)/Dpx(t) fitted with g=9.8 gives D = 7.6-7.7 cm consistently for early, late and whole
  segments (cy=540 is the only principal row giving consistent segments). Release time 0.064 s.

## Answers
- 2997 diameter: depth-aware 7.60 cm; 50-fps global fit (a=9537) 7.71 cm; early 60-fps fit 7.72;
  60-fps whole fit (perspective-biased) 8.27. Answer 7.7 cm. Confidence medium-high.
- 2998 v(0.2): physical 1.33 m/s (=9.8*(0.2-0.064)); 50-fps fit 1.42; naive 50-fps finite diffs
  1.08-1.27. Answer 1.34. Confidence medium.
- 2999 v(0.4): physical 3.29; 50-fps fit 3.38; finite diffs 2.7-2.96. Answer 3.28. Confidence medium.
- 3002 displacement 0.3->0.4: 274.5 px; physical 0.281 m, 50fit 0.282. Answer 0.282. Confidence high.
- 3000/3001 distance from desk: desk back edge at y=973; ball bottom ~1003 at frame 24 (reflection on
  glossy desk suggests contact ~1005). Physical gap (ball bottom to contact level): 0.365 m @0.4 s,
  0.646 m @0.3 s; centre-to-edge 0.383 / 0.662; bottom-to-edge 0.344 / 0.624. Answers 0.37 / 0.645.
  Confidence medium.
