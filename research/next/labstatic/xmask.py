"""Connected components of non-black pixels in lab x renders (SAM-masked, black background)."""
import sys, cv2, numpy as np
sys.path.insert(0, 'research/next/labstatic')
from frames import read_all

def comps(vid, n, thr=25, min_area=150):
    fr = read_all(vid)[n]
    g = fr.max(axis=2)
    m = (g > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k, lab, st, cen = cv2.connectedComponentsWithStats(m)
    out = []
    for i in range(1, k):
        x, y, w, h, a = st[i]
        if a >= min_area:
            out.append(dict(i=i, x=x, y=y, w=w, h=h, area=a, cx=cen[i][0], cy=cen[i][1]))
    return out, lab

if __name__ == '__main__':
    vid = sys.argv[1]; n = int(sys.argv[2])
    out, _ = comps(vid, n)
    for o in out:
        print(o)
