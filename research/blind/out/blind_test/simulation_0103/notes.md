# simulation_0103 (A2MS, 2D planar, prior: shark acceleration = 1 m/s^2)

Scene: side view; red fishing boat (AH805) moving right at constant speed on the water surface; shark below
(cut-away underwater region) swimming left and accelerating. 54 frames @ 24 fps. Frames 0 and 1 are identical
(first frame static/duplicated); motion visible from frame 1 on.

## Scale
- Shark tracked by sub-pixel template matching (dorsal fin, tail; body as a check), frames 1-53.
  Quadratic fit x(t)=x0+v0 t+a t^2/2 with t=frame/24: a = 85.98 px/s^2 (tail 86.06, fin 85.90, body 85.70;
  sub-range fits 85.5-86.4). => 1 m = 85.98 px at the shark plane.
- Fitted v0 = 172.1 px/s, v0/a = 2.001 s (round), and x(1/24) ~ 0 = observed frame-1 position, so the t=frame/24
  clock is the right one; frame 0 is a held duplicate.

## Answers
- 202 shark speed at 0 s: v0 = 172.1/85.98 = 2.00 m/s (high confidence, assumes GT = initial speed).
- 203 boat speed at 1 s: bow tip (centre-line point) moves 17.865 px/frame constant (frames 1-53, red mask)
  = 428.8 px/s -> 4.99 m/s. Template on near-side hull features gives ~1.7% higher (near-side parallax),
  bow tip used as it is on the centre line. Boat at same scale as shark (round 5.0 m/s and 10 m length support it).
- 204 boat length: background-difference extent at frame 53: x 594..1452 -> ~856-858 px (stern extreme is the
  transom corner, small perspective correction ~0.5%) -> 9.95 m (high confidence).
- 205 shark length: masks over all frames, median width ~279 px (half-max edges 278) -> 3.24 m.
- 206 shark height: dorsal-fin tip (y~851.5) to pectoral-fin bottom (y~955) ~104-106 px -> 1.22 m.
- 207 distance shark-boat at 0.5 s (frame 12): horizontal centre separation ~1281 px = 14.9 m; vertical depends
  on boat origin (keel/waterline y~640 -> 15.2 m; hull centre -> 15.6 m; bbox centre incl. mast -> ~16.4 m).
  Chose 15.6 m as a compromise (medium confidence). Assumes shark and boat in same depth plane.
