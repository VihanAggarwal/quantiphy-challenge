"""Astronaut mask track (bright suit on black sky / grey ground) for simulation_0171 / 0172.
Per frame: centroid of the bright (suit) mask above the ground line, bbox, and the backpack-free torso width proxy.
usage: astro_track.py video_id"""
import sys, cv2, numpy as np, json
vid = sys.argv[1]
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
fr = np.array(fr)
bg = np.median(fr, axis=0)
out = []
for i, g in enumerate(fr):
    d = np.abs(g.astype(int) - bg)
    m = ((d > 40) & (g > 120)).astype(np.uint8)   # bright suit pixels that differ from background
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, 4])
    # merge components close to the biggest one (limbs split by dark joints)
    x0, y0, w, h = st[k, :4]
    keep = [j for j in range(1, n) if st[j, 4] > 30 and abs(cen[j][0] - cen[k][0]) < 1.5 * max(w, h) and abs(cen[j][1] - cen[k][1]) < 1.5 * max(w, h)]
    mm = np.isin(lab, keep)
    ys, xs = np.nonzero(mm)
    out.append(dict(i=i, cx=float(xs.mean()), cy=float(ys.mean()), x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()), area=int(mm.sum())))
json.dump(out, open(f'/home/user/quantiphy-challenge/research/next/sim3audit/group2/{vid}_astro.json', 'w'))
for o in out[::4]:
    print(o)
