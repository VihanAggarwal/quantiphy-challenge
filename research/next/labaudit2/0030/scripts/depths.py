"""Per-frame range of the ball by three routes, on the capture clock (n = k + (k>=12) + (k>=36)).
 plane: ball centre on the plane 3.5 cm above the table top (round-1 plane 'gm', camera 19.6 cm above the top);
 size : centre range from the silhouette's ellipse minor axis (blur-free direction), f*0.07/minor, with the off-axis
        correction (range = Z_axis * |ray|; minor axis ~ f*2R/range for a sphere seen off-axis);
 stated anchors (surface ranges): n5 0.8715, n10 1.166, n15 1.372, n20 1.315."""
import numpy as np, json
D = '/home/user/quantiphy-challenge/research/next/labaudit2/0030/'
f = 711.; c = np.array([640., 360.])
PL = json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/plane.json'))
M = json.load(open(D + 'track_mask.json'))
R = 0.035
ANCH = {5: 0.8715, 10: 1.166, 15: 1.372, 20: 1.315}


def cap(k): return k + (k >= 12) + (k >= 36)


def ray(x, y): return np.array([(x - c[0]) / f, (y - c[1]) / f, 1.])


def unit(x, y):
    v = ray(x, y); return v / np.linalg.norm(v)


def plane_pos(x, y, R=R, pl='gm'):
    n = np.array(PL[pl]['n']); d = PL[pl]['d']; rr = ray(x, y); return (d + R) / (n @ rr) * rr


def size_range(minor):
    return f * 2 * R / minor


if __name__ == '__main__':
    rows = []
    for k, m in enumerate(M):
        if m is None:
            continue
        n = cap(k)
        pp = plane_pos(m['mx'], m['my'])
        rp = np.linalg.norm(pp)
        minor = min(m['el'][1])
        rs = size_range(minor)
        rows.append((k, n, m['mx'], m['my'], rp, rs, minor, m['bot'] - m['top'] + 1))
        a = ANCH.get(n)
        print(f"v{k:2d} n{n:2d} ({m['mx']:6.1f},{m['my']:5.1f}) plane ctr {rp:.3f} surf {rp-R:.3f} | size ctr {rs:.3f} surf {rs-R:.3f} (minor {minor:.1f}, h {m['bot']-m['top']+1})"
              + (f"  | STATED surf {a:.4f}  ratio stated/plane_surf {a/(rp-R):.3f} stated/size_surf {a/(rs-R):.3f}" if a else ''))
