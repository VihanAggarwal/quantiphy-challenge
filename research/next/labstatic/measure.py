"""Reproduce the measurements behind build_candidate.py (test inputs only) plus two method checks.

Pixel positions come from the colour/mask tracks in tools/ (yellow.py = HSV blob track, white.py = bright blob
against the clip median, book24.py = teal book track, xmask.py = x-render masks) and from crops read by eye
(frames.py). Fixed lab camera: f = 711 px at 1280 px, principal point (640, 360); a stated depth is used as the
range of the clicked point.

Method checks (no label enters any answer):
  * validation captured_0021x ping-pong displacement 1.0-1.4 s: own track + stated depths -> 48.6 cm (label 49.69)
  * validation captured_0041x soccer displacement 1.5-1.6 s: own track -> 0.49-0.53 m (label 0.6116; stated speed
    5.21 m/s agrees with ~0.52)
  * held-out stated basketball (23.2 cm) in 0052 / 0053, px * range / f with the off-axis stretch removed:
    22.6-23.9 / 21.4-22.3
  * test captured_0001 / 0006 / 0014 / 0032 / 0031 / 0018 displacement or distance rows that the base already gets
    from depth-anchored geometry reproduce within 1-4 % (23.1 vs 23.2, 36.1-36.6 vs 36.3, 15.8-17.1 vs 16.2-16.6,
    29.7-30.2 vs 29.5, 22.9 vs 22.9, 225-230 vs 229-230): the remaining failures are the families below.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import P, dist, ray  # noqa: E402

F = 711.0


def line_point(P0, P1, u, v):
    d = (P1 - P0) / np.linalg.norm(P1 - P0)
    r = ray(u, v, F)
    A = np.array([[d @ d, -d @ r], [-d @ r, r @ r]]); b = np.array([-(P0 @ d), P0 @ r])
    s, _ = np.linalg.solve(A, b)
    return P0 + s * d


def fam_A():  # 0024 distance travelled by the book
    P1, P2 = P(747, 394, 1.0685), P(680, 443, 0.977)          # stated anchors at 1.0 s / 1.2 s on the colour track
    S = line_point(P1, P2, 790, 369)                           # start (book at rest at the top, n 0-18)
    out = {}
    for re in (0.93, 0.97, 1.0):
        E = P(570, 482, re)                                    # end (book at rest on the table, n >= 36)
        B = P(615, 478, 0.99)                                  # slope foot (stated slope near end)
        out[re] = (dist(S, E) * 100, (dist(S, B) + dist(B, E)) * 100)
    return dict(start_range=np.linalg.norm(S), straight_and_polyline_cm=out)


def fam_B():  # 0028 maximum height of the ping-pong ball
    A = P(750, 298, 1.4115)                                    # apex n~32 (t 1.3 s)
    res = {}
    for bv in (408, 398):                                      # bounce n~26 / the 1.1 s frame
        Bp = P(738, bv, 1.557)
        res[bv] = dict(vertical_cm=-(A - Bp)[1] * 100, euclid_cm=dist(A, Bp) * 100)
    return res


def fam_C():  # 0023 book displacement 1.0-1.6 s
    Pt, Pb = P(585, 357, 1.201), P(585, 483, 0.9555)           # stated slope ends
    X10 = line_point(Pt, Pb, 588, 383)
    P16 = P(565, 496, 0.851)
    by_size = P(588, 383, 0.851 * 176 / 130)
    return dict(slope_len_cm=dist(Pt, Pb) * 100, r10=np.linalg.norm(X10), disp_line_cm=dist(X10, P16) * 100,
                disp_size_cm=dist(by_size, P16) * 100)


def floor_0054a():
    best = None
    for th in np.radians(np.arange(0, 40, 0.02)):
        n = np.array([0, np.cos(th), np.sin(th)])
        hs = [n @ P(u, v, r) + 0.116 for u, v, r in ((344, 600, 2.3557), (584, 674, 1.81))]
        e = abs(hs[0] - hs[1])
        if best is None or e < best[0]:
            best = (e, th, np.mean(hs))
    return best[1], best[2]


def on_floor(u, v, th, h, hgt):
    n = np.array([0, np.cos(th), np.sin(th)]); d = np.array([(u - 640) / F, (v - 360) / F, 1.0])
    return (h - hgt) / (n @ d) * d


def fam_DE():  # 0054a orange-soccer distance at 1.0 s (D, not applied) and soccer displacement 1.0-1.4 s (E)
    th, h = floor_0054a()
    O = P(584, 674, 1.81)
    out = dict(pitch_deg=np.degrees(th), cam_height=h, feet_range=np.linalg.norm(on_floor(655, 525, th, h, 0.0)))
    out["D_dist_m"] = [dist(O, on_floor(u, v, th, h, R)) for (u, v) in ((150, 610), (153, 608)) for R in (0.09, 0.11)]
    out["E_disp_m"] = [dist(on_floor(*a, th, h, R), on_floor(*b, th, h, R)) for a in ((150, 610), (145, 615))
                       for b in ((68, 668), (75, 662), (62, 672)) for R in (0.09, 0.11)]
    return out


def fam_F():  # trashbin height in 0052 (upright, stated 2.977 m)
    px = 587.5 - 484
    th_c = np.arctan(np.hypot(85, 175) / F); th_v = np.arctan(175 / F)
    return dict(naive_cm=px * 2.977 / F * 100, z_cm=px * 2.977 * np.cos(th_c) / F * 100,
                label_style_cm=2.977 * px / F * np.cos(th_v) ** 2 * 100)


def fam_H():  # slope width
    return dict(c0023_bottom=dist(P(494, 480, 0.9555), P(677, 480, 0.9555)) * 100,
                c0023_top=dist(P(516, 362, 1.201), P(660, 362, 1.201)) * 100,
                c0014_top=dist(P(500, 314, 1.854), P(592, 303, 1.854)) * 100,
                c0014_bottom=dist(P(509, 422, 1.701), P(609, 408, 1.701)) * 100)


def fam_I():  # 0023/0024 book length
    Pt, Pb = P(585, 357, 1.201), P(585, 483, 0.9555)
    r24 = np.linalg.norm(line_point(Pt, Pb, 588, 383))
    a, b = line_point(Pt, Pb, 588, 363), line_point(Pt, Pb, 588, 403)
    return dict(rest_cm=dist(P(477, 496, 0.851), P(655, 496, 0.851)) * 100,
                on_slope_cm=dist(P(523, 383, r24), P(653, 383, r24)) * 100, along_slope_cm=dist(a, b) * 100)


def checks():
    return dict(val_0021x_disp_cm=dist(P(727.1, 418.2, 1.511), P(751.4, 451.2, 1.03)) * 100,
                val_0041x_disp_m=[dist(P(585, 612, 2.544), P(595, 661, 2.074)), dist(P(577, 574, 2.544), P(595, 661, 2.074))])


if __name__ == "__main__":
    np.set_printoptions(precision=3, suppress=True)
    for name, fn in (("A", fam_A), ("B", fam_B), ("C", fam_C), ("D/E", fam_DE), ("F", fam_F), ("H", fam_H), ("I", fam_I),
                     ("checks", checks)):
        print(name, fn())
