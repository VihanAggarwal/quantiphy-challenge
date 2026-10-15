# internet_0049 notes
Scene: pergola with picnic tables. Handheld camera with a slight drift (phase-correlation shift up to (-15, +27) quarter-res px). A CG-looking rider on a scooter crosses left to right, frames ~140-265, just behind the front row of tables.
Scale: I tracked the rider's x by hand in stabilized half-res frames (every 10 frames). A linear fit gives 15.5 half-px/frame = 466 half-px/s. 3.8/466 = 0.00815 m/half-px (122.7 px/m) at the rider's depth. The rider's ground y stays about constant along the path.
Perspective: the vanishing point of the floor seams (7 Hough lines) gives a horizon of y=385 (frame 195, band half-res coords). The rider's ground contact is ~555, so camera height c = 170/122.7 = 1.385 m. An object whose ground contact is at y_g has (y_g-385)/c px per metre. Heights use h = c*(y_g-y_top)/(y_g-yh).
Measurements (frame 195, half-res band coords):
- Rider: head 332, sole 537, 205 px -> 1.67 m (medium-high confidence).
- Gray table: top 468, ground under the front edge ~581 -> 0.80 m. Gray bench: top 516, feet 589 -> 0.50 m. Answered 0.79 and 0.48 (medium).
- Middle brown table: top 470, ground ~586 -> 0.80 m. Length 834-1184 = 350 px at 145 px/m -> 2.41 m (medium).
- Canopy: front pillar foot 590, top fascia 52 -> 3.63 m at the pillar's depth. The fascia overhangs toward the camera, so I answered 3.5 (medium-low).
- Centre-to-centre distance, gray table (x~231) to middle brown table (x~1009): 778 px at ~145 px/m -> 5.3 m (medium-low; edge-to-edge would be ~3.4).
If the scorer applied one scale with no perspective correction, the front-row answers would be ~20% larger.
