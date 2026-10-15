# internet_0024 - desk scene (top-down, 3840x2160, 30 frames @25 fps)

Scale: AirPods-style case lying on its back (port edge visible). GrabCut silhouette minAreaRect = 230.1 x 197.1 px;
width (port-edge direction) 197 px = 45 mm -> 0.2284 mm/px (single 2D scale).
Cross-check: MacBook Air 13" front edge (line fits + corner intersections) = 1424 px -> 32.5 cm, exactly the real spec.
Camera is tilted (~15-20 deg; laptop side edges converge to VP ~(-4400,-11800); mug rim ellipse 432x396 px), so vertical
image directions are slightly foreshortened and the top of frame is farther. Answers use the pixel/prior scale (2D convention).

- 2121 case length: 230 px -> 52.5 mm; real AirPods 53.5 (54.3 if scaled to 45 width). Answer 53. Confidence high.
- 2122 pencil: end-to-tip 766 px (saturation profile along axis) -> 17.5 cm (tilt-corrected ~18). Answer 17.6. Medium-high.
- 2123 mug diameter: outer rim at frame 0, horizontal 432 px (9.9 cm), vertical 396 px (9.0 cm); rim ~9.5 cm above table so
  real diameter ~9.1 cm. Answer 9.6. Medium.
- 2124 laptop longest side: 1424 px -> 32.5 cm. High.
- 2125 wallet (brown planner) long side: top edge 735 px, bottom edge 767 px -> 16.8-17.5 cm. Answer 17.3. Medium.
- 2126 mug velocity at 0.50 s: mug lifted and moved down-left. Coffee-centroid track and frame-to-frame template matching agree:
  11->12 = 58-61 px/frame, 12->13 = 65.4 px/frame (t=0.50 s is midway between frames 12 and 13) -> 33-37 cm/s. Answer 36. Medium.
Scripts in work/.
