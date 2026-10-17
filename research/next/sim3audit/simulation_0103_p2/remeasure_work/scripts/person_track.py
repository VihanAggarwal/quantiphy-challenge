import sys, numpy as np, cv2
from vio import *
v=sys.argv[1]; box=[int(x) for x in sys.argv[2].split(',')]  # x0,y0,x1,y1 search box
fr=load(v)
x0,y0,x1,y1=box
out=[]
for k,f in enumerate(fr):
    sub=f[y0:y1,x0:x1].astype(int)
    m=(sub.min(axis=2)<235)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    if n<2: out.append([k]+[np.nan]*6); continue
    i=1+np.argmax(st[1:,4])
    ys,xs=np.nonzero(lab==i)
    out.append([k, xs.mean()+x0, ys.mean()+y0, xs.min()+x0, xs.max()+x0, ys.min()+y0, ys.max()+y0])
out=np.array(out)
np.set_printoptions(suppress=True, precision=1, linewidth=150)
print(out[::4])
np.savetxt(W+'person_%s.txt'%v, out, fmt='%.2f')
