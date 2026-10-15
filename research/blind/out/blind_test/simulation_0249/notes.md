# simulation_0249 (V2MS, top-down 2D, 24 fps, 50 frames)
Scene: top-down view; brown horse (back/trailing, top), tan horse (front/leading), small brown rabbit; all walking +x. Frame 49 loops back (brown horse), ignored.
Segmentation: colour mask (R-B>12 or dark) + muzzle edge detection (light-grey muzzle missed by colour mask).
Scale: brown horse centroid slope 4.40 px/frame (edges 4.25/4.46) = 105.6 px/s; 0.874 m/s -> 0.008277 m/px.
- 842 back horse length: median 254 px (incl. muzzle) -> 2.10 m (med conf)
- 844 front horse length: median 306 px -> 2.53 m (med conf)
- 845 rabbit length: ~61 px -> 0.505 m (med-low conf, small object)
- 843 front horse speed: 7.75 px/frame mean (local 16-32: 7.79) -> 1.54 m/s (med conf)
- 846 rabbit speed: 7.65 mean, 7.9 local -> 1.53 m/s (med conf, hopping gait)
