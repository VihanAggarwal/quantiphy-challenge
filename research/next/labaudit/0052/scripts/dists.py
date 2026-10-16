import numpy as np, cv2, sys
sys.path.insert(0,'scripts')
from xmask import xmask
F=711.;CX=640;CY=360
def P(u,v,r,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return r*d/np.linalg.norm(d)
def D(a,b): return float(np.linalg.norm(a-b))
m=xmask(30)  # ball has left the start area? use frame 0 for shoe/bb (static)
m0=xmask(0)
k,lab,st,cen=cv2.connectedComponentsWithStats(m0,8)
for i in range(1,k):
    x,y,w,h,a=st[i]
    if a>1000: print('comp',i,'bbox',x,y,w,h,'centroid',cen[i].round(1),'bbox centre',(x+(w-1)/2,y+(h-1)/2))
# bin: columns 680-776 rows 484-591 from o-render; centroid of blue pixels in o-render median
med=cv2.imread('med_late_o.png').astype(int)
b,g,r=med[...,0],med[...,1],med[...,2]
blue=(b>45)&(b-r>30)&(b-g>15)
blue[:470]=0;blue[600:]=0;blue[:,:670]=0;blue[:,790:]=0
ys,xs=np.where(blue); print('bin blue centroid',xs.mean().round(1),ys.mean().round(1),'extent',xs.min(),xs.max(),ys.min(),ys.max())
R={'yoga':2.612,'shoe':2.231,'bin':2.977,'bb':1.9365}
shoe_c=[(284,656.5),(285,654),(281,660)]
bb_c=[(801.5,671.5),(803,668)]
bin_c=[(728,538),(xs.mean(),ys.mean()),(728,545)]
yoga0_c=[(612,508),(610.3,507.3)]
r0s=[2.95,3.01,3.08,3.14]
def rng(lst): return '%.3f-%.3f'%(min(lst),max(lst))
for f in (700,711,722):
    bbS=[D(P(*a,R['bb'],f),P(*s,R['shoe'],f)) for a in bb_c for s in shoe_c]
    binS=[D(P(*a,R['bin'],f),P(*s,R['shoe'],f)) for a in bin_c for s in shoe_c]
    binB=[D(P(*a,R['bin'],f),P(*s,R['bb'],f)) for a in bin_c for s in bb_c]
    yS=[D(P(*a,r0,f),P(*s,R['shoe'],f)) for a in yoga0_c for s in shoe_c for r0 in r0s]
    print('f=%d bb-shoe %s | bin-shoe %s | bin-bb %s | yoga0-shoe %s'%(f,rng(bbS),rng(binS),rng(binB),rng(yS)))
for r0 in r0s:
    print('r0=%.2f yoga0-shoe %.3f'%(r0,D(P(612,508,r0),P(284,656.5,2.231))))
