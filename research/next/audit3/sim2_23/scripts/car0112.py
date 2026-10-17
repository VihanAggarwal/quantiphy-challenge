import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0112_segmented.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=f.astype(int)
    m=(g.min(axis=2)<200)  # non-white
    sub=m[:538]
    ys,xs=np.nonzero(sub)
    # column profile to find car extent
    cols=np.nonzero(sub[380:538].sum(0)>2)[0]
    rows=np.nonzero(sub[:, :].sum(1)>2)[0]
    print(i, cols.min() if len(cols) else -1, cols.max() if len(cols) else -1, rows.min() if len(rows) else -1, rows.max() if len(rows) else -1)
    i+=1
