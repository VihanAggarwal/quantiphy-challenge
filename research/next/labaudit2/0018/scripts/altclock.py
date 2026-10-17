"""Configurations under the alternative clock readings: v48 (clip end) and v39 (t0 = 1.36 -> 3.0 s), plus end-of-clip speeds,
and the persons' feet rows for the floor check. Depth per object: floor model (h 0.875) at the object's bottom when on the floor,
otherwise the same per-object surface Z as labelstyle.py."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
R = json.load(open(OUT + 'track_refined.json'))
H = 0.875
def zfloor(ybot): return H * F / (ybot - CY)
def P(u, v, z): return z * ray(u, v)
Zc = dict(box=2.61, soccer=2.749, tennis=2.21, pine=1.80)
for v in (39, 48):
    pts = {}
    for n in ['box', 'soccer', 'tennis', 'pine']:
        r = R[n][str(v)]
        z = Zc[n]
        if n == 'box': z = zfloor(r['bot'])           # box on the floor at v39/v48
        if n == 'pine': z = zfloor(r['bot'])
        pts[n] = P(r['mx'], r['my'], z)
        print(f"v{v} {n:7s} ({r['mx']:.0f},{r['my']:.0f}) bot {r['bot']} Z {z:.2f}")
    for a, b in [('box', 'soccer'), ('box', 'pine'), ('box', 'tennis'), ('tennis', 'soccer'), ('pine', 'soccer'), ('pine', 'tennis')]:
        print(f"   v{v} {a}-{b}: {np.linalg.norm(pts[a]-pts[b])*100:.0f} cm")
# end-of-clip speeds, v47->v48 (both on c49->c50, consecutive)
for n in ['box', 'soccer', 'tennis', 'pine']:
    r0, r1 = R[n]['47'], R[n]['48']
    z = Zc[n] if n not in ('box', 'pine') else zfloor(r1['bot'])
    s = 25 * np.linalg.norm(P(r1['mx'], r1['my'], z) - P(r0['mx'], r0['my'], z))
    r2 = R[n]['46']
    s2 = 25 * np.linalg.norm(P(r0['mx'], r0['my'], z) - P(r2['mx'], r2['my'], z))
    print(f"end speed {n}: v46->47 {s2*100:.0f}  v47->48 {s*100:.0f} cm/s")
# persons' feet: lowest matte rows in left (x 330-430) and right (x 890-1010) person columns, v24
fx = frames('x')
m = (np.abs(fx[24].astype(int) - 255).max(2) > 30)
for name, (a, b) in dict(far=(330, 430), near=(890, 1010)).items():
    ys = np.where(m[:, a:b].any(1))[0]
    print(name, 'person matte bottom y', ys.max())
