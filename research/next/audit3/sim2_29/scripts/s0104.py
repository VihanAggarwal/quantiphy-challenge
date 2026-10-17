from util import *
fr=frames('simulation_0104',gray=True)
bgv=None
ys=[]
for i in sorted(fr):
    g=fr[i].astype(np.float32)
    col=g[:,900:1050].mean(axis=1)
    bgval=np.median(col[:200])
    d=np.abs(col-bgval)
    idx=np.where(d>25)[0]
    y0=idx[0]
    # subpixel: interpolate crossing of half of step
    ys.append(y0)
    # horizontal extent of phone at row y0+3
    row=g[y0+4,:]; bgr=np.median(g[y0+4,:300]); w=np.where(np.abs(row-bgr)>20)[0]
    print(i,y0, w.min() if len(w) else -1, w.max() if len(w) else -1)
