# Lab audit, family 0052 (captured_0052 / 0052s / 0052x): 24 rows, all D3

**Result: no fix.** Every row is within about 10% of my label emulation, or the evidence for a change does not reach the
15% threshold. The yoga-ball diameter is borderline; it is flagged below but not proposed.

## The scene
- Fixed lab camera, nearly level.
  - Wall seams (`scripts/seams.py`) give the vertical VP far below the image: pitch about 0.6-0.9 deg down, roll about -0.8 deg.
  - The pinhole model uses f = 711 px and principal point (640, 360).
- A person crouches at the back. A 55 cm-class grey yoga ball sits beside them, static from n0 to n19 at about (612, 507).
  It is then pushed toward the camera and leaves at the bottom left (n38+).
- The other objects are static all clip long:
  - a blue recycling bin at the back right,
  - a white Adidas-style shoe on the floor at the front left,
  - a basketball on the floor at the front right.
- The s and x renders are SAM2 composites of the same frames: the same pixels, with a snowy or green background. The x
  render gives clean masks, about 1.5-3 px generous per side.
- Object pixels:

  | object | source | bbox | centre |
  |---|---|---|---|
  | basketball | x-mask | x 756-847, y 624-719 | (801.7, 671.9) |
  | shoe | x-mask | x 250-318, y 626-687 | (284, 656.5) |
  | bin, back-rim silhouette | o-render | 485.5 | |
  | bin, front-rim highlight | o-render | 497.5 | |
  | bin, bottom | o-render | 590.5 | |
  | bin, x extent | o-render | 681-776 | |

## Checks on f, the depth convention and the floor
- **Basketball check.** I used the stated range 1.9365 as the front-surface range, with centre distance = range + R and
  23.2 cm. This predicts a horizontal silhouette width of 92.2 px, and 92 px is observed (x-mask). The range convention and
  f = 711 hold.
  - The measured physical diameter is 22.2-23.2 cm.
  - The click-style value (edge clicks back-projected at the centre's surface range) is 21-22 cm. So the stated 23.2 is
    the physical size, not a click value.
- **Floor height below the camera** (`scripts/floor.py`):

  | anchor | pitch 0 deg | pitch 1 deg |
  |---|---|---|
  | basketball | 0.923 | 0.955 |
  | bin front-bottom edge (Z = 2.867 from the stated 2.977) | 0.929 | 0.979 |
  | yoga ball at t0 | 0.943 | 0.999 |

  These anchors agree. The shoe's stated 2.231 is the outlier (0.82-0.85).
  - The floor geometry puts the shoe click at range 2.53-2.55. The stated shoe ToF reads about 12% short.
  - The labels presumably use 2.231, so the label emulation below keeps it.

## Row by row
| qid (o/s/x) | question | current | route 1 | route 2 | verdict |
|---|---|---|---|---|---|
| 2783/2791/2799 | initial yoga-shoe distance | 1.339/1.308/1.308 | label emulation: yoga ball at n0 (612, 508) with range r0 from the sphere geometry, shoe at 2.231 -> 1.32-1.37 (1.46 with the generous x-mask width) | floor plane (h from the basketball and bin anchors) -> 1.23-1.26 | OK |
| 2784/2792/2800 | trashbin height (cm) | 37.67 | stated range, front-face Z 2.867, front rim 497.5 to bottom 590.5 (93 px) -> 37.5 | floor plane -> 37.4-37.7 | OK (see below) |
| 2785/2793/2801 | shoe length (cm) | 23.1/24.3/22.7 | floor plane, toe (251, 684) to heel (318.5, 651) -> 20-27, central about 23 | label emulation with a ToF bias -> 17-23 (the shoe lies nearly along the line of sight, so this is sensitive) | OK |
| 2786/2794/2802 | yoga ball diameter (cm) | 47.86 | physical, from the stated range at t=1.0 -> 54.9 (visual edges) to 56-58 (gradient edges / x-mask) | physical, floor route at n0 -> 52.9-55.1; same ball in 0047 (t=1.0, 2.4985 m) about 56, in 0061 (t=0.6, 2.133 m) 54.3 | borderline, not fixed (see below) |
| 2787/2795/2803 | basketball diameter (cm) | 23.2 (fact) | physical from the stated range: 22.2-23.2 | | OK |
| 2788/2796/2804 | basketball-shoe distance | 1.417/1.450/1.422 | label emulation (stated ranges, centres) -> 1.336-1.346 | floor plane -> 1.51-1.52 | OK (both within about 7% of current) |
| 2789/2797/2805 | bin-shoe distance | 1.617/1.648/1.623 | label emulation -> 1.625-1.659 | floor plane -> 1.59-1.60 | OK |
| 2790/2798/2806 | bin-basketball distance | 1.091/1.090/1.090 | label emulation -> 1.123-1.149 | floor plane -> 1.07-1.12 | OK |

Distances are centre to centre, varying the click pixels by a few px and f over 700-722 (`scripts/dists.py`, `scripts/route2.py`).

### Initial yoga-ball range (needed for the first row)
- At n0 the ball is sharp and static. Its angular diameter is 2a0 = 0.1673-0.170 rad, from the o-render edges: left 551.5,
  right 673.5, top 443.5, bottom 572.
- With R from t=1.0, the centre distance is D0 = 3.23-3.28, so the surface range at the centre click is r0 = 2.95-3.01.
  The x-mask widths give 3.14.
- The floor route gives r0 = 2.89-2.95.
- The current 1.31-1.34 matches r0 of about 2.97-3.0.

### Trashbin height
- The camera (h about 0.95 m) is well above the rim, so the top silhouette at y 485.5 must be the back rim, and the front
  rim is lower.
  - The highlight line at 497.5 is the front rim. The 12 px band between them is the inner back wall.
  - The predicted back-rim to front-rim separation for a bin about 26 cm deep is 12 px, which matches.
- The physical height is 37.4-37.7 cm by both routes, which matches the current 37.67. The bin is also consistent with a
  standard 28 qt deskside bin.
- A label that clicked the top silhouette (the back-rim pixel) would read 41-45. That is the 41.5 that labstatic F proposed
  and the merge verifier rejected. No evidence here that 37.67 is wrong.

### Yoga ball diameter (borderline, not proposed)
- The physical size is well determined at about 55 cm, a standard 55 cm ball, by:
  - the sphere geometry with the stated 2.612 at n24,
  - the floor route at n0,
  - and the same ball measured in 0047 and 0061.
- A click-style label (edge clicks at the stated surface range) would read 49.7-52.2 here, 50.6 in 0047 and 48.3 in 0061.
- The current 47.857 is pooled (physb2) from captured_0047's geometric estimate (r_geo 47.857). That is a click-style /
  surface-range value, and it is the same number now used in 0052 and 0061.
- Against the physical 55 the current value is 14.9% low. That is just under the 15% bar, and the label convention (physical
  vs click) is not settled. Against the click-style value it is only 4-8% low.
- A value of about 52 would be at least as good as 47.86 under either convention, but it is below the 15% threshold, so no
  fix is proposed.
- If the orchestrator has independent evidence that lab size labels are physical prop sizes (the stated basketball 23.2 is
  physical; click-style reads 21-22 here), then about 55 for 2786/2794/2802 (and for 0061's yoga rows) would be the move.

## Files
- `scripts/extract.py` - frames (o_/s_/x_NN.png)
- `scripts/seams.py` - wall-seam lines and VP
- `scripts/xmask.py` - green-screen masks
- `scripts/conefit.py`, `scripts/edges.py`, `scripts/sphere_size.py` - sphere silhouette and diameter
- `scripts/yoga_floor.py` - floor-route ball radius
- `scripts/dists.py` - label-emulation distances
- `scripts/floor.py` - floor height per anchor
- `scripts/route2.py` - floor-plane distances and bin height
- `scripts/shoe.py` - shoe length
- Crops: `g_yoga00.png`, `g_yoga24.png`, `g_bin.png`, `g_shoe_o.png`, `g_shoe_x.png`, `g47_24.png`, `g61_14.png`
- Sheets: `sheet_o.png`, `sheet_roll.png`, `renders_cmp.png`
