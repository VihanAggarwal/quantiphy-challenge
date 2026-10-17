"""Label-style and physical ball speeds for 0037 at t=1.0 s (c25=v24 -> c26=v25) and t=1.4 s (c35=v34 -> c36=v35).
Clock: c = v + (v>=12) + (v>=36) (double-length step v35->v36 confirmed in the track).
Clicked centres: blob centroid or capsule centre (x and s renders); for v35 (bottom of the ball hidden by the jar lid)
also the hop-C model position (what a clicker who sees the whole ball would click).
Range at the clicks:
  c25: stated 1.055 m (surface).
  other frames: (S) size route: smoothed capsule diameter d(c) (line in capture time over the clean in-flight frames
       v22-27, v30-34, v37-40), R_surf(c) = 1.055 * d(25)/d(c) [anchored to the stated range at c25];
       (G) gravity route: per-hop ballistic fit (g=9.8 along the table normal, f=711/735) gives the centre-range
       change R(c)-R(25) for hop B; for hop C the anchor is carried by the fit's own range rescaled by
       1.055/R_fit_B(c25).
Physical: speed of the fitted ballistic curve at c25 / c35."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import OUT, cap, ray, F
from ballistic import fit_hop
from bouncefit import run as bounce_run

TR = json.load(open(OUT + '/track.json'))
CP = json.load(open(OUT + '/capsule.json'))
R25 = 1.055


def clicks(r, mode):
    if mode == 'cent':
        return {int(n): (e['u'], e['v']) for n, e in TR[r].items()}
    return {int(n): (e['cu'], e['cv']) for n, e in CP[r].items()}


def size_line(r, frames_=tuple(range(22, 28)) + tuple(range(30, 35)) + tuple(range(37, 41))):
    c = np.array([cap(n) for n in frames_]); d = np.array([CP[r][str(n)]['r2'] for n in frames_])
    p = np.polyfit(c, 1.0 / d, 1)            # 1/d linear in time ~ range linear in time
    return p


def fd(P0, P1, dc=1):
    return np.linalg.norm(P1 - P0) * 25 / dc * 100


if __name__ == '__main__':
    rows = []
    for r in ('x', 's'):
        p = size_line(r)
        dS = lambda c: 1.0 / np.polyval(p, c)
        rr = dS(25) / dS(26)
        print(f'[{r}] size line: d(c25)={dS(25):.2f}px d(c26)={dS(26):.2f} d(c35)={dS(35):.2f} d(c36)={dS(36):.2f}; '
              f'size range-rate at c25 {(R25 + .02) * (dS(25) / dS(26) - 1) * 2500:+.1f} cm/s, at c35 {(R25 + .02) * dS(25) * (1 / dS(36) - 1 / dS(35)) * 2500:+.1f} cm/s')
        # gravity fits
        G = {}
        for f in (711, 735):
            for hb in ((21, 28), (22, 28), (21, 27)):
                B = fit_hop(r, list(range(*hb)), f=f)
                RB = lambda c, B=B: np.linalg.norm(B['pos']((c - B['tref']) / 25))
                G[(f, 'B', hb)] = (RB(26) - RB(25), RB(25), B)
            for hc in ((30, 35), (29, 35), (30, 36), (29, 36)):
                C = fit_hop(r, list(range(*hc)), f=f)
                RC = lambda c, C=C: np.linalg.norm(C['pos']((c - C['tref']) / 25))
                G[(f, 'C', hc)] = (RC(36) - RC(35), RC(35), C)
        for mode in ('cent', 'caps'):
            ck = clicks(r, mode)
            u24, u25, u34, u35 = ck[24], ck[25], ck[34], ck[35]
            # ---- t = 1.0 s
            P25 = R25 * ray(*u24)
            out = []
            out.append(('S', fd(P25, (R25 * dS(25) / dS(26)) * ray(*u25))))
            for k, (dR, R0, B) in G.items():
                if k[1] != 'B':
                    continue
                out.append((f'G{k[0]}{k[2]}', fd(P25, (R25 + dR) * ray(*u25))))
            out.append(('noRate', fd(P25, R25 * ray(*u25))))
            print(f'[{r} {mode}] v(1.0) label-style FD c25->26: ' + '  '.join(f'{a}={b:.1f}' for a, b in out))
            # ---- t = 1.4 s: range at c35 from size route anchored at c25, or gravity hop-C fit rescaled
            RS35 = R25 * dS(25) / dS(35); RS36 = R25 * dS(25) / dS(36)
            out = [('S', fd(RS35 * ray(*u34), RS36 * ray(*u35)))]
            for k, (dR, R0, C) in G.items():
                if k[1] != 'C':
                    continue
                # surface range at c35 = fit centre range - 2cm (plane/gravity scale); also ToF-anchored scale variant
                Rs35 = R0 - 0.02
                out.append((f'G{k[0]}{k[2]}', fd(Rs35 * ray(*u34), (Rs35 + dR) * ray(*u35))))
            print(f'[{r} {mode}] v(1.4) label-style FD c35->36 (v35 click as tracked): ' + '  '.join(f'{a}={b:.1f}' for a, b in out))
            # model position of v35 (hop C fit v30-34 projected to c36) as the 'whole-ball' click
            for f in (711, 735):
                C = G[(f, 'C', (30, 35))][2]
                X36 = C['pos']((36 - C['tref']) / 25)
                um = (f * X36[0] / X36[2] + 640, f * X36[1] / X36[2] + 360)
                X35 = C['pos']((35 - C['tref']) / 25)
                um34 = (f * X35[0] / X35[2] + 640, f * X35[1] / X35[2] + 360)
                Rs35 = np.linalg.norm(X35) - 0.02; Rs36 = np.linalg.norm(X36) - 0.02
                v_model = fd(Rs35 * ray(*u34), Rs36 * ray(*um))
                v_modelS = fd(RS35 * ray(*u34), RS36 * ray(*um))
                print(f'    f{f}: hop-C model v34 ({um34[0]:.1f},{um34[1]:.1f}) v35 ({um[0]:.1f},{um[1]:.1f}) vs tracked v35 {u35[0]:.1f},{u35[1]:.1f}; '
                      f'FD with model v35 click: G-range {v_model:.1f}, S-range {v_modelS:.1f}')
        # physical speeds from fits
        for k, (dR, R0, Fh) in G.items():
            c = 25 if k[1] == 'B' else 35
            V = Fh['vel']((c - Fh['tref']) / 25)
            X = Fh['pos']((c - Fh['tref']) / 25)
            print(f'[{r}] phys {k}: |V(c{c})|={np.linalg.norm(V)*100:.1f} cm/s radial {V@X/np.linalg.norm(X)*100:+.1f} range {np.linalg.norm(X):.3f} rms {Fh["rms"]:.2f}')
