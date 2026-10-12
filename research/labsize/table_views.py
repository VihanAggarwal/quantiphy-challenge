"""Lab table measured in many views by metric rectification (test inputs only).

Per view: refined table-top corners (rough corners read from grid overlays), the plane's scale from each
depth_info anchor lying on / above the table (ball centre = front-surface range + R, R above the plane;
an object's box bottom-centre at its range; table-end entries at the front corners), and both side lengths
at several focal lengths. The table is one rigid object, so (a) its sides must agree across views and
(b) views where the long side runs across the image vs in depth scale differently with f: the f at which
the views agree is a label-free focal-length estimate.

    .venv/bin/python research/labsize/table_views.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import rect  # noqa: E402
from corners import draw, frame, refine, table_mask  # noqa: E402
from plane import C, anchor_scale  # noqa: E402

# corners: back-left, back-right, front-right, front-left; front: edges with the dark side band
# anchors: (pixel, range m, height above table m, ball radius m)
VIEWS = {
    "captured_0036x": dict(rough=[(417, 442), (753, 449), (984, 592), (197, 585)], front=(2,),
                           anchors={"pingpong t0.9": ((569, 456), 1.01, 0, 0.02)}),
    "captured_0029x": dict(rough=[(440, 452), (905, 466), (1120, 585), (208, 540)], front=(2,),
                           anchors={"tennis t1.0": ((818, 466), 0.901, 0, 0.0335)}),
    "captured_0022x": dict(rough=[(282, 415), (598, 364), (668, 517), (228, 607)], front=(2,),
                           anchors={"pingpong t0.6": ((435, 394), 1.751, 0, 0.02),
                                    "pingpong t0.8": ((432, 414), 1.687, 0, 0.02),
                                    "pingpong t1.2": ((423, 457), 1.526, 0, 0.02)}),
    "captured_0014x": dict(rough=[(448, 340), (657, 311), (727, 460), (428, 500)], front=(2,),
                           anchors={"pen": ((468, 436), 1.6725, 0.006, 0), "book": ((653, 414), 1.665, 0.015, 0)}),
    "captured_0038x": dict(rough=[(452, 450), (950, 472), (1135, 595), (210, 540)], front=(2,),
                           anchors={"card": ((569, 542), 0.6867, 0, 0), "poker": ((684, 498), 0.9035, 0, 0),
                                    "cup": ((759, 498), 0.874, 0, 0), "bottle": ((665, 480), 0.9998, 0, 0),
                                    "ball t1.4": ((724, 510), 0.716, 0, 0.02)}),
    "captured_0037x": dict(rough=[(430, 455), (935, 470), (1138, 592), (210, 543)], front=(2,),
                           anchors={"card": ((563, 539), 0.679, 0, 0), "poker": ((684, 499), 0.905, 0, 0),
                                    "cup": ((776, 504), 0.845, 0, 0), "jar": ((471, 483), 1.008, 0, 0),
                                    "tape": ((557, 475), 1.038, 0, 0)}),
    "captured_0023x": dict(rough=[(455, 442), (770, 442), (922, 525), (282, 530)], front=(2,),
                           anchors={"table_left@FL": (None, 0.704, 0, 0), "table_right@FR": (None, 0.725, 0, 0),
                                    "slope_near": ((585, 483), 0.9555, 0, 0)}),
    "captured_0021x": dict(rough=[(576, 430), (847, 440), (959, 496), (464, 484)], front=(2,),
                           anchors={"pingpong t1.0": ((727, 419), 1.511, 0, 0.02),
                                    "pingpong t1.4": ((751, 452), 1.03, 0, 0.02)}),
}
FS = (690, 711, 722, 740, 763, 790)


def measure(views=VIEWS, fs=FS):
    rows = []
    for v, cfg in views.items():
        fr = frame(v)
        cr, _, st = refine(fr, table_mask(fr), cfg["rough"], front=cfg["front"])
        draw(fr, [(np.array(cfg["rough"], float), (255, 0, 0)), (cr, (0, 0, 255))], "quad_" + v)
        for f in fs:
            X = rect.parallelogram(cr, f, C)
            n = np.cross(X[1] - X[0], X[3] - X[0])
            n /= np.linalg.norm(n)
            if n @ X[0] > 0:
                n = -n
            sh = rect.shape(cr, f, C)
            for name, (uv, r, h, R) in cfg["anchors"].items():
                if uv is None:
                    uv = cr[3] if "FL" in name else cr[2]
                s = anchor_scale(X, n, uv, r, f, h=h, R=R)
                a = np.linalg.norm(X[1] - X[0]) * s  # back edge
                b = np.linalg.norm(X[3] - X[0]) * s  # left edge
                # which side runs across the image: compare image-x spans
                across = "back" if abs(cr[1][0] - cr[0][0]) > abs(cr[3][0] - cr[0][0]) else "left"
                rows.append(dict(view=v, f=f, anchor=name, back=a, left=b, long=max(a, b), short=min(a, b),
                                 long_across=(a > b) == (across == "back"), angle=sh["angle"],
                                 cam_h=abs(n @ X[0]) * s))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    d = measure()
    d.to_csv(Path(__file__).parent / "out/table_views.csv", index=False)
    per = d.groupby(["view", "f"]).agg(long=("long", "median"), short=("short", "median"), n=("long", "size"),
                                       long_across=("long_across", "first"), angle=("angle", "first"),
                                       sd_scale=("long", lambda x: float(np.std(np.log(x)))))
    print((per.round(3)).to_string())
    print("\nacross-view agreement by f (sd of log over views; medians):")
    for f, g in per.groupby(level="f"):
        print(f, "long: med %.1f sd %.3f | short: med %.1f sd %.3f" % (
            100 * g.long.median(), np.std(np.log(g.long)), 100 * g.short.median(), np.std(np.log(g.short))),
              "| long-across views: %.1f, long-in-depth views: %.1f" % (
                  100 * g[g.long_across].long.median(), 100 * g[~g.long_across].long.median()))
