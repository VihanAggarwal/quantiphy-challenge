# simulation_0259 (A2MC, 1920x1080, 40 frames @30fps)
Scene: red/cream takeaway cup falls vertically (x~855) from top of frame onto a table at frame ~15; static camera.
## Scale
- Cup track (bg-diff vs frame 39, frames 5-14) quadratic fit: a = 6.93 px/frame^2 (6.88-7.00 across fits), release t0 ~ -0.1 frame.
- s = 9.8 / (6.93*900) = 1.571e-3 m/px at cup depth (cup lands near back of table; all table objects have bottoms at y~871 -> same depth).
## Perspective
- Horizon from window lines on right side wall: VP ~(1460, 722). Consistent check: back-left table leg at x~680 predicted from depth ratio 1.207 (back edge y865 vs front edge y895) with VP x=1460 -> 691. Good.
- Cup centre depth / table front edge depth = (895-722)/(869.5-722) = 1.173.
## Measurements (px -> m)
- Cup height: 64 px (near horizon in frame 14; 65.7 at rest incl. perspective) -> 0.1006
- Plant: height 62.5 px raw (-1.5 persp) -> 0.0958; width (leaves) 48.1 px -> 0.0756
- Table front edge 518.5..1539 = 1020.5 px at front-edge depth -> 1020.5*s/1.173 = 1.367
- AC front 132..637 = 505.5 px -> 0.794 at cup depth; AC assumed slightly closer than cup (against wall) -> 0.77 (low confidence)
- iPhone right of plant: x-extent 51.2 px -> 0.080; lying with long side roughly in depth; answered 0.078 (between AABB x-extent and true 0.0715)
- Mug height 54.7 raw -> 53.2 px -> 0.0836
- Bag x-extent 224.3 px -> 0.352, front slightly closer -> 0.35
## Speeds (backward diff, free fall from ~frame 0)
- t=0.2 (frame 6): a*(5.6 frames) -> 1.83 m/s; t=0.4 (frame 12): 11.6 frames -> 3.79 m/s (direct centroid diffs: 1.84, 3.78)
## Confidence: speeds high; cup/plant/mug/bag medium-high; table medium (perspective correction); AC low-medium; phone medium.
