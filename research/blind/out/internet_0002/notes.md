# internet_0002 — red pickup on multi-lane highway (nadir drone view, 3840x2160, 36 frames, fps 24)

## Setup
- Camera: near-nadir drone shot, essentially static (phase correlation drift < 2 px over 36 frames).
- Median background of all frames -> lane dashes detected (bright components). Lane-line centre rows (y at x~1900):
  355, 664, 990, 1309, 1616, 1946 -> mean lane width 318.2 px; red car's lane (L3-L4) 317-326 px depending on x (~320).
  Scale used: 3.66 m / ~319 px = 0.01147 m/px.
- Silver sedan at the top shows its side face -> camera height estimate H ~ 30 m (roof parallax ~5% for a 1.5 m high feature).
- Lens: dashes ~2.5% longer at image edges than at centre (mild distortion); centre frames preferred for size.

## Red car (crew-cab pickup with grey tonneau cover), moving +x, slight lane change toward the lower lane
- Tracking: red HSV mask (centroid), front edge from background difference, rear edge from shadow->car gray transition,
  checked with overlays (frames/ov.png) and zoomed crops.
- Length: centre frames 12-24 apparent length 515-520 px by threshold detector; visual check shows tailgate rim ~10-15 px
  further back -> ~527-530 px -> 6.04-6.08 m pixel-based. Physical (height-parallax corrected) ~5.85 m. Answer 6.0 m.
- Width: body (cab/bed rails) ~185-188 px -> 2.12-2.16 m; mirrors ~219 px (2.5 m); parallax-corrected body ~2.0 m.
  Answer 2.15 m (body, pixel-based).
- Speed: red centroid 106.6 px/frame along x (+4.7 px/frame in y) over frames 0-29; rear edge 106.2, front edge 105.1;
  -> ~106.4 px/frame x 24 fps x 0.01147 = 29.3 m/s pixel-based; ~27.9 m/s if corrected for roof height parallax.
  Answer 29.0 m/s.

## Confidence
- 2019 length 6.0 m: medium-high (±4%).
- 2020 width 2.15 m: medium (body vs mirrors ambiguity; ±8%).
- 2021 speed 29.0 m/s: medium-high (±4%).
