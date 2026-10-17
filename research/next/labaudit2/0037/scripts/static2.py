"""Static re-check with edges read from colour profiles on the x-render median (static.py's bboxes include the table,
so the bottoms are taken where the object colour meets the brown table top):
  cup   column 774: rim back 377, rim front ~381, bottom-front contact 503.5 (dark line at 504)
  poker column 689: apex 416, feet 496-499.5 (round 1), 498 used
  tape  rows 440-455: half-max edges 519.5 / 592.0 (73 px); column 556: top-face back 430, bottom-front 473.5
Route A = label-style (clicks at the two ends, ToF ~ stated range); route B = table plane (PnP)."""
import sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from static import height_on_vertical

for f in (711, 735):
    print(f'--- f={f}')
    for top in (377, 381):
        H, R = height_on_vertical(774, 503.5, 774, top, f)
        print(f'cup  top {top}: route A {(503.5 - top) * 0.845 / f * 100:.2f} cm | route B plane {H * 100:.2f} cm')
    for bot in (496, 498, 499.5):
        H, R = height_on_vertical(689, bot, 689, 416, f)
        print(f'poker feet {bot}: route A {(bot - 416) * 0.905 / f * 100:.2f} cm | route B plane {H * 100:.2f} cm')
    w = 592.0 - 519.5
    print(f'tape diameter: {w:.1f}px -> at stated front 1.038: {w * 1.038 / f * 100:.2f} cm; at axis range ~1.09: {w * 1.09 / f * 100:.2f} cm')
    print(f'tape band (front face 440 -> 473.5, 33.5 px) at 1.038: {33.5 * 1.038 / f * 100:.2f} cm')
