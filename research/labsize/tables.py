"""Lab table top (and other planar rectangles) measured by metric rectification. Test inputs only.

Corners: rough corners read by eye from grid overlays (out/grid_*.png), refined by RANSAC lines on the
uniform-background render's table mask (corners.refine); every refined quad is drawn to out/quad_*.png.
For each view: the f where the corner angle is 90 deg (yawed views constrain f), and the aspect ratio
(back-edge / side-edge) at f = 711 / 722 / 763 px."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import rect  # noqa: E402
from corners import draw, frame, refine, table_mask  # noqa: E402
from zoom import zoom_sheet  # noqa: E402

C = (640.0, 360.0)
# order: back-left, back-right, front-right, front-left (front edges have the darker side band)
VIEWS = {
    "captured_0036x": ([(417, 442), (753, 449), (984, 592), (197, 585)], (2,)),
    "captured_0029x": ([(440, 452), (905, 466), (1120, 585), (208, 540)], (2,)),
    "captured_0022x": ([(282, 415), (598, 364), (668, 517), (228, 607)], (2,)),
    "captured_0024x": ([(415, 468), (881, 452), (1138, 505), (645, 607)], (2, 3)),
    "captured_0014x": ([(448, 340), (657, 311), (727, 460), (428, 500)], (2,)),
}


def run(views=VIEWS, out=Path(__file__).parent / "out"):
    import cv2
    res = {}
    for v, (rough, front) in views.items():
        fr = frame(v)
        m = table_mask(fr)
        cr, lines, st = refine(fr, m, rough, front=front)
        draw(fr, [(np.array(rough, float), (255, 0, 0)), (cr, (0, 0, 255))], "quad_" + v)
        zoom_sheet(cv2.imread(str(out / f"corners_quad_{v}.png")), cr, str(out / f"zquad_{v}.png"))
        roots, fs, angs = rect.f_right_angle(cr, C)
        sh = {f: rect.shape(cr, f, C) for f in (711, 722, 763)}
        res[v] = dict(corners=cr, roots=[r for r in roots if np.isfinite(r)], stats=st,
                      aspect={f: s["aspect"] for f, s in sh.items()}, angle={f: s["angle"] for f, s in sh.items()},
                      dang_dlogf=(rect.shape(cr, 800, C)["angle"] - rect.shape(cr, 650, C)["angle"]) / np.log(800 / 650))
        print(v, "corners", np.round(cr, 1).tolist(), "edge inliers", st)
        print("   f(90deg):", np.round(res[v]["roots"], 0), " dAngle/dlnf=%.1f" % res[v]["dang_dlogf"],
              " aspect@711/722/763: %s" % [round(a, 3) for a in res[v]["aspect"].values()],
              " angle@722: %.1f" % res[v]["angle"][722])
    return res


if __name__ == "__main__":
    run()
