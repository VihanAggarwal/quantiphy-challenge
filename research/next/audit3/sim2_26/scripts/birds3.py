import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0088')
sky=np.median(np.stack(F[::3]),axis=0)
L=[];S=[]
for i in range(16,25):  # crow alone in frame, eagle gone
    g=cv2.cvtColor(F[i],cv2.COLOR_BGR2GRAY).astype(float)
    gs=cv2.cvtColor(sky.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(float)
    dark=gs-g   # crow is darker than sky
    ys,xs=np.nonzero(dark>dark.max()*0.5)
    # body length along x: full extent using half-max of global darkness
    colprof=dark.max(0); rowprof=dark.max(1)
    def ext(p):
        thr=p.max()*0.5; idx=np.nonzero(p>thr)[0]; a,b=idx[0],idx[-1]
        return (b+(p[b]-thr)/(p[b]-p[b+1]))-(a-1+(thr-p[a-1])/(p[a]-p[a-1]))
    L.append(ext(colprof)); S.append(ext(rowprof))
    print(i,round(L[-1],1),round(S[-1],1))
s=0.0062595
print('crow len px median',np.median(L),'m',np.median(L)*s,'span max px',max(S),max(S)*s)
