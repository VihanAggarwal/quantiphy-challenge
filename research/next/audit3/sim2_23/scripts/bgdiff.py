import cv2, numpy as np, sys
# per-frame bbox of the moving object via difference from a temporal median background
v = sys.argv[1]; thr = float(sys.argv[2]) if len(sys.argv) > 2 else 25
roi = list(map(int, sys.argv[3:7])) if len(sys.argv) > 6 else None
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
fr = []
while True:
    ok, f = c.read()
    if not ok: break
    g = cv2.resize(f, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)  # half-res for memory
    fr.append(g)
fr = np.array(fr)
bg = np.median(fr, axis=0).astype(np.float32)
for i, f in enumerate(fr):
    d = np.abs(f.astype(np.float32) - bg).max(axis=2)
    m = (d > thr).astype(np.uint8)
    if roi: 
        mm = np.zeros_like(m); x0,y0,x1,y1 = [r//2 for r in roi]; mm[y0:y1,x0:x1] = m[y0:y1,x0:x1]; m = mm
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2,2),np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2: print(i, 'none'); continue
    k = 1 + np.argmax(st[1:, 4])
    # merge components close to the largest
    x,y,w,h,a = st[k]
    big = [j for j in range(1,n) if st[j,4] > 30 and st[j,0] < x+w+40 and st[j,0]+st[j,2] > x-40 and st[j,1] < y+h+40 and st[j,1]+st[j,3] > y-40]
    xs = min(st[j,0] for j in big); ys = min(st[j,1] for j in big)
    xe = max(st[j,0]+st[j,2] for j in big); ye = max(st[j,1]+st[j,3] for j in big)
    print(i, 2*xs, 2*ys, 2*(xe-xs), 2*(ye-ys), round(2*cen[k][0],1), round(2*cen[k][1],1))
