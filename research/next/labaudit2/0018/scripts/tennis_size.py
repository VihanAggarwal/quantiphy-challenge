"""Tennis-ball diameter in px from half-max colour-difference profiles (o render, clean bg) and x-matte; Z = 6.7 cm * f / d."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
fo = frames('').astype(np.float32); fx = frames('x')
bg = np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg0018.npy')
R = json.load(open(OUT + 'track_refined.json'))['tennis']
def halfwidth(prof):
    p = prof - np.median(np.r_[prof[:4], prof[-4:]]); mx = p.max(); i = np.argmax(p)
    h = mx / 2
    l = i
    while l > 0 and p[l] > h: l -= 1
    r = i
    while r < len(p) - 1 and p[r] > h: r += 1
    # subpixel
    lx = l + (h - p[l]) / (p[l + 1] - p[l]); rx = r - 1 + (p[r - 1] - h) / (p[r - 1] - p[r])
    return rx - lx
for v in [41, 42, 43, 44, 45, 46, 47, 48]:
    r = R[str(v)]; cx, cy = int(round(r['mx'])), int(round(r['my']))
    win = fo[v, cy - 3:cy + 4, cx - 20:cx + 21]; b = bg[cy - 3:cy + 4, cx - 20:cx + 21]
    d = np.abs(win - b).sum(2).mean(0)
    win2 = fo[v, cy - 20:cy + 21, cx - 3:cx + 4]; b2 = bg[cy - 20:cy + 21, cx - 3:cx + 4]
    d2 = np.abs(win2 - b2).sum(2).mean(1)
    mrow = (np.abs(fx[v, cy - 1:cy + 2, cx - 20:cx + 21].astype(int) - 255).max(2) > 30).sum(1)
    w = halfwidth(d); h = halfwidth(d2)
    print(f"v{v} centre=({r['mx']:.0f},{r['my']:.0f}) halfmax width={w:.1f}px height={h:.1f}px  matte rows={mrow.tolist()}  Z(w)={0.067*F/w:.2f} Z(h)={0.067*F/h:.2f}")
# held v20..24: tennis ball partly behind fingers on its right; use left edge to ball top/bottom (vertical extent)
for v in [20, 22, 24]:
    cx, cy = 763, 249
    win2 = fo[v, cy - 20:cy + 21, cx - 6:cx - 1]
    g = np.abs(win2 - np.array([180, 180, 180], np.float32)).sum(2)
    # vertical profile of 'greenness' (G - B)
    gb = (fo[v, cy - 20:cy + 21, cx - 6:cx] [..., 1] - fo[v, cy - 20:cy + 21, cx - 6:cx][..., 0]).mean(1)
    gh = (fo[v, cy - 3:cy + 4, cx - 20:cx + 21][..., 1] - fo[v, cy - 3:cy + 4, cx - 20:cx + 21][..., 0]).mean(0)
    print(f"held v{v}: G-B vertical halfmax={halfwidth(gb):.1f}px horizontal={halfwidth(gh):.1f}px")
