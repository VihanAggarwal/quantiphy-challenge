import cv2, numpy as np, sys
for vid in sys.argv[1:]:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
    prev=None; d=[]
    while True:
        ok,img=cap.read()
        if not ok: break
        g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None: d.append(np.abs(g-prev).mean())
        prev=g
    d=np.array(d)
    print(vid, len(d)+1, 'smallest diffs (idx->idx+1):', [(int(i),round(float(d[i]),3)) for i in np.argsort(d)[:5]])
