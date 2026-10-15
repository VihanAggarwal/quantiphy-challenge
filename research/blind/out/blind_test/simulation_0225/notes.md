# simulation_0225 (V2MC, prior: cat speed 1.041 m/s)
- Static camera, 50 frames @24fps. Cat tracked by median-background subtraction (scripts/track2.py); centroid moves 5.467 px/frame horizontally, constant y and size (no depth motion) -> 131.2 px/s -> 0.007934 m/px at the cat's depth.
- Camera is level: patio joint lines converge to VP ~(940,540) (scripts/joints.py, manual line fits) -> horizon y~540. Ground scale m/px = h/(y_ground-540); cat ground y~917.5 -> h ~2.99 scene units.
- Cat length: median mask width 106 px -> 0.841 m. Height (tail tip to ground) ~74.5 px -> 0.591 m. Confidence medium-high (pose dependent).
- Beach chair (front-middle) front frame 180 px wide, front-leg ground y=901 -> 2.99*180/361 = 1.49 m. Confidence medium.
- Pool coping tiles: joint spacing 150 px on front face (top edge y=927) -> 1.159 m; patio pavers spacing 147.5 px at y=922 -> 1.155 m. Answer 1.157. Confidence medium-high.
