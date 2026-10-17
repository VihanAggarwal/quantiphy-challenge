import cv2,numpy as np
D='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/frames/'
bg=cv2.imread(D+'orig_bg.png'); g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(float)
def bottom_edge(u, v0=598, v1=622):
    col=g[v0:v1,u]
    # last row where intensity < thr going downward, then crossing to bright floor
    lo=col[:8].min(); hi=col[-4:].mean()
    thr=(lo+hi)/2
    # find last index where col<thr
    idx=np.nonzero(col<thr)[0]
    if len(idx)==0: return np.nan
    k=idx.max()
    if k+1>=len(col): return np.nan
    # subpixel interpolate between k and k+1
    a,b=col[k],col[k+1]
    return v0+k+(thr-a)/(b-a)+0.0
def top_edge(u, v0=455, v1=480):
    col=g[v0:v1,u]
    return col
for name,us in (('R',range(668,782,2)),('L',range(296,402,2))):
    vs=np.array([bottom_edge(u) for u in us]); us=np.array(list(us))
    m=np.isfinite(vs)
    p=np.polyfit(us[m],vs[m],1)
    print(name,'bottom edge fit slope %.4f, v at ends %.2f..%.2f'%(p[0],np.polyval(p,us[0]),np.polyval(p,us[-1])))
    print('  ',' '.join('%d:%.1f'%(u,v) for u,v in zip(us[::3],vs[::3])))
