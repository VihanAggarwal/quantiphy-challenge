# Audit sim2_06: family simulation_0228 (0225, 0225_seg, 0226, 0227, 0227_seg, 0228)

Scene: pool deck with a black cat walking +x, beach chairs, pavers, and a pink flamingo swim ring in the pool (0227/0228 only).
- 0225 / 0227 (+ segmented twins): level front camera (horizon y~540), deck edge (top of pool wall) at y~928, cat paws y~921.
- 0226 / 0228: top-down camera.
- Prior in every clip: cat speed 1.041 m/s (constant walk).

## Scales (own tracking, scripts in work/)
| clip | cat px/frame (median-bg centroid fit) | m/px at cat |
|---|---|---|
| 0225_seg (front) | 5.449 | 0.00796 |
| 0226 (top) | 5.457 | 0.00795 |
| 0228 (top) | 5.458 | 0.00795 |
| 0225 / 0227 raw | agents 5.47 / 5.40 | 0.0079-0.0080 |

Front view m/px at the deck edge (y=928) from ground-plane depth ratio: 0.00796*(921-540)/(928-540) = 0.00782.
Paver joint pitch: top-down 144.6 px (9 intervals, 574->1875) -> 1.149 m; front, at deck edge 148.7 px (converging-line sampling).

## Rows checked (all 35 scored rows)
| qid | clip | quantity | current | quick check | status |
|---|---|---|---|---|---|
| 696/1950 | 0225/_seg | cat length | 0.841 | front seg W med 106.5 px -> 0.848 | ok |
| 700 | 0226 | cat length | 0.859 | top W med 107 px -> 0.851 | ok |
| 703/1954 | 0227/_seg | cat length | 0.833 | 0.848 (same footage as 0225 front) | ok |
| 710 | 0228 | cat length | 0.865 | top W med 108 px -> 0.858 | ok |
| 697/1951, 704/1955 | front | cat height | 0.591/0.593 | seg H med 76 px -> 0.605 | ok |
| 698/1952, 705/1956 | front | chair width | 1.49/1.54 | front legs 182-186 px at m/px 0.00838 (leg y~902) -> 1.53-1.56 | ok |
| 701, 711 | top | chair width | 1.526/1.53 | seat 192-195 px -> 1.50-1.55 | ok |
| 699, 702, 706 | all | pool tile width | 1.157/1.15/1.166 | top paver pitch 144.6 px -> 1.149; front wall joints 149.8 px*0.00782 -> 1.171 | ok |
| 712 | 0228 | paving stone width | 1.13 | 1.149 pitch (1.13 after joint gap) | ok |
| 707/1958, 713 | 0227/0228 | ring length | 1.165/1.14 | top W med 145 px -> 1.153 (x1.00-1.02 water plane); front 158.5 px | ok |
| 708/1959 | 0227 | ring height | 0.90 | head top y887, ~0.83 m above water at ring-centre depth + submerged part; visible span 132 px -> <=0.95 | ok (unverifiable to better than ~10%) |
| 709/1960 | 0227/_seg | ring speed 0.5 s | 1.74 | front seg quad-fit backward-diff 9.45 px/f * 24 * 0.0071-0.0073 -> 1.61-1.66 | ~7% high, below 15% fix bar, left |
| 714 | 0228 | ring speed 0.5 s | 1.62 | top 8.3 px/f * 24 * 0.00795*(1.00-1.03) -> 1.58-1.63 | ok |
| 1953 | 0225_seg | pool-wall marking spacing | 1.9 | 1.16 | FIX |
| 1957 | 0227_seg | pool-wall marking spacing | 1.5 | 1.16 | FIX |
| 1961-1965 | 0227_seg | red general chess speed/accel | 2.27/2.1/0.24/1.68/1.77 | no chess piece in the clip (only cat, chairs, ring; checked all frames for red/non-white blobs) | unverifiable, left |

Ring motion is the same scripted motion in 0227 (front) and 0228 (top): front/top total displacement ratio 430/386 = 1.11, speed profiles match in shape. Both routes give ~1.62 m/s at t=0.5 s; 0227's 1.74 is ~7% high (agent used the right edge's 9.9 px/f and 0.00735 m/px), not enough to qualify as a fix.

## Fixes
### 1953 (0225_segmented) and 1957 (0227_segmented): spacing between the markings on the pool wall -> 1.16 m
- Why the current answers are wrong: the background (pool wall included) is removed in the segmented clips, so these were not measured (no notes exist), and the two twins of the same scene disagree (1.9 vs 1.5).
- The non-segmented twins (0225/0227, identical camera) show vertical joints on the pool wall face at x = 333, 482, 633, 781, 931, 1082, 1232, 1382, 1533, 1681, 1831 -> pitch 149.8 px. These are the "markings".
- Route A (front view, its own cat-speed scale): 149.8 px * 0.00782 m/px (deck edge depth) = 1.171 m.
- Route B (top-down 0226/0228, its own cat-speed scale): paver pitch 144.6 px * 0.00795 = 1.149 m; the front view shows wall-joint pitch / paver pitch at the same edge = 149.8/148.7 = 1.007 -> 1.157 m.
- The routes agree within 1.2%; they also match the siblings' answered pool-tile width (1.157, 1.15, 1.166). Proposed 1.16 (current values are 64% and 29% off).

No other row met the fix criteria.
