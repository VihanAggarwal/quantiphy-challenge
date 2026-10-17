# Independent re-measure: sim2_01, qid 601 (simulation_0215, length of the TV stand, m)

Result: **1.815 m** (route A, anchored to 0215's own prior: 1.811; route B, front-view sibling 0216 with its own prior: 1.822).
Confidence: medium-high. The current value of 1.52 is too short. It put the stand's right end around x~1152, but that end is hidden
under the lampshade, which is centred at x~1190 in the top view.

Inputs used: the 0215 video, plus siblings 0214/0217 (the same top-down camera: same cat pixels and the same stand left end and lamp position)
and 0216/0216_segmented (fronto-parallel view of the same stand). Agent notes were read for 0214-0217 only.
I did not read sim2_01/notes.md.

## Top-view scale (0215)
- Cat template tracking, frame to frame (head and torso; 0214 is the same motion and has no occlusion): 10.93 px/frame, or 262.3 px/s.
  The 0.94 m/s prior gives 0.0035835 m/px at the cat's tracked-feature height.
- Feature height: back ~0.29 m, head/ears ~0.32-0.35 m (front view: silhouette top versus a floor contact at y~1012). I used h_c = 0.30.
- Camera height H ~8.65 m, from two checks: the lampshade top opening is displaced radially by 13.7 px over a 0.26 m rise at r=390,
  and the stand front-face strip runs y 283.5 -> 292 for h 0.449 -> 0.168. Range considered: 8-10 m.
- s(stand top, h=0.449) = 0.0035835*(H-0.449)/(H-0.30) = 0.003520 m/px, varying by +-0.3% over the H range and +-0.6% for h_c +-0.05.

## Route A (0215 pixels + front-view position of the hidden right end)
- Top view, projected to the stand-top plane: the stand left end is at x=709.6 (a sharp edge at all rows).
  The lamp axis is at x=1178.2: the shade-rim circle-fit centre (1190.5, 225.4, r 73, h~0.89) and the top opening (1198.1, 214.0, h~1.15),
  each reprojected to h=0.449, agree within 1 px.
  The vase axis is at 760.0. Lamp minus left end = 468.6 px = 1.6495 m.
- Front view 0216: the front-face ends are at x=651.3 and 1423.6 (772.3 px). The lamp axis is at x=1343.7 (centre of the base column).
  The vase axis is at x=732.2. The top surface front edge is at y=794.7 and the back edge at y=776, giving Z_b/Z_f=1.0792.
  Combined with the 0.403 m stand depth from the top view, this gives Z_f ~5.09 m.
  The lamp and vase are 0.1475 m and 0.1295 m behind the front face (from the top view), so k = 1.0290 and 1.0254.
  - The lamp axis is 0.1623 m inside the right end (fraction along the stand p = 0.9109).
  - Check: vase axis minus left end is 0.1773 m in the front view and 0.1774 m in the top view.
    Lamp minus vase is 1.483 m in the front view and 1.472 m in the top view. The two views agree within 0.7%.
- L = 1.6495 + 0.1623 = 1.812 m, or 1.6495/0.9109 = 1.811 m.

## Route B (0216 front view, own cat prior)
- Cat head and torso template tracking: 17.47 px/frame, giving 0.002242 m/px at the cat's depth. The midline paw contact is at y~1012
  (near paws ~1018-1020, far paws ~1005-1008). Horizon y=540, since verticals are vertical.
  This gives camera height 1.058 m. The stand front frame meets the floor at y=988.5, so s_front = 0.0023595 m/px.
  - Independent check: the gap between the cat's path and the stand front is 0.247 m in the front view and 0.249 m in the top view.
- L = 772.3 * 0.0023595 = 1.822 m. A cat-contact y of 1008 or 1016 gives 1.806 or 1.838.

## Occlusion bound (top view)
For L = 1.81, the right-end corners fall 5-10 px inside the shade outline. No dark stand or front-face pixels show beside the shade:
the region right of it at y 175-291 reads as carpet. This gives a soft upper bound of L < ~1.83 m.

## Sibling cross-checks
- The original notes give 0214 = 485 px (1.68) and 0217 = ~522 px (~1.8). Both are the same camera as 0215, and their right ends were
  guessed under the lamp. 0216 gives 1.823, consistent with this result.
- 0216 TV length: front 0.964 m, top (top edge 805-1099 px at h~1.09) 0.957 m.
  TV feet spacing: front 0.781 m, top 0.778 m. These support a common scale.

Files: track_tmpl.py (template tracking), track_cat.py, top_circles.py (shade and vase circle fits), and the crops viewed (*.png).
