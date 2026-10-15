# simulation_0226 (2D top-down, 24 fps, 50 frames)
- Black cat walks +x along pool edge; dark-threshold mask, centroid & bbox tracked per frame (track.py).
- Pixel speed: 5.456 px/frame (centroid and leading edge agree, 5.47) -> 130.95 px/s. Scale = 1.041/130.95 = 0.00795 m/px.
- Cat length incl. tail: bbox 105-111 px (median ~108; verified on zoomed crop 640->749 px) -> 0.859 m. Confidence medium-high.
- Beach chair width: base width of 3 front chairs 191-193 px (backrest top looks ~203 px, raised/perspective) -> 192 px -> 1.526 m. Confidence medium (chair is elevated above ground plane; perspective could shrink true value a bit).
- Pool tile horizontal width: grout-line spacing 144.6 px (periodic, consistent) -> 1.150 m. Confidence high.
