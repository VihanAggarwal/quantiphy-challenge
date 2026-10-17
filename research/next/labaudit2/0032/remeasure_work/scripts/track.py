import cv2, numpy as np, sys, json
src = sys.argv[1]
cap = cv2.VideoCapture(src)
out = []
i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    H,S,V = hsv[...,0].astype(int), hsv[...,1].astype(int), hsv[...,2].astype(int)
    roi = np.zeros(S.shape, bool); roi[380:520, 450:1000] = True
    white = (S < 60) & (V > 170) & roi
    yellow = (H > 20) & (H < 40) & (S > 120) & (V > 120) & roi
    rec = {'i': i}
    for name, m in (('w', white), ('y', yellow)):
        m8 = m.astype(np.uint8)
        m8 = cv2.morphologyEx(m8, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m8)
        if n > 1:
            k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
            x0,y0,w,h,a = st[k]
            rec[name] = [float(cen[k][0]), float(cen[k][1]), int(w), int(h), int(a), int(x0), int(y0)]
    out.append(rec); i += 1
for r in out:
    print(r['i'], r.get('w'), r.get('y'))
