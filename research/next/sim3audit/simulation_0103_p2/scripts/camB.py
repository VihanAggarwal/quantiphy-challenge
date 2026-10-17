import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from geom import *; from reg import *
fr=frames('simulation_0023_segmented')
# boat: largest component in rows>290, x<560 region at f24
def boatmask(im):
    m=fgmask(im); n,l,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    bm=np.zeros_like(m)
    for kk in range(1,n):
        X,Y,W,H,A=st[kk]
        if A>=10 and X>=x-10 and X+W<=x+w+60 and Y>=y-120 and Y+H<=y+h+10: bm|=(l==kk)
    return bm,(x,y,w,h)
bm24,b24=boatmask(fr[24]); bm48,b48=boatmask(fr[48])
hull24=bm24.copy(); hull24[:b24[1]+b24[3]-110]=False
ys,xs=np.where(hull24); c24=(xs.mean(),ys.mean())
print('boat box 24',b24,'48',b48,'hull centroid 24',np.round(c24,1))
g=lambda im: cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
a=g(fr[24]); b=g(fr[48]); x,y,w,h=b24
T=a[y-3:y+h+3,x-3:x+w+3]; R=cv2.matchTemplate(b,T,cv2.TM_SQDIFF_NORMED); mn,_,ml,_=cv2.minMaxLoc(R)
px,py=ml
l_,c_,r_=R[py,px-1],R[py,px],R[py,px+1]; dx=0.5*(l_-r_)/(l_-2*c_+r_); u_,c_,d_=R[py-1,px],R[py,px],R[py+1,px]; dy=0.5*(u_-d_)/(u_-2*c_+d_)
disp=(px+dx-(x-3),py+dy-(y-3)); print('boat disp 24->48',np.round(disp,2),'score',round(mn,4))
# scale change? use multi-scale
best=None
for s in np.linspace(0.95,1.0,26):
    Ts=cv2.resize(T,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    R=cv2.matchTemplate(b,Ts,cv2.TM_SQDIFF_NORMED); mn,_,ml,_=cv2.minMaxLoc(R)
    if best is None or mn<best[0]: best=(mn,s,ml,Ts.shape)
print('best scale',round(best[1],4),'score',round(best[0],4))
p1=c24; p2=(c24[0]+disp[0],c24[1]+disp[1])
for conv in ['range']:
    f=solve_f(p1,p2,103.1570,106.0906,4.0,480,480,conv)
    print('boat-chord f',round(f,1))
fe=solve_f((471.1,372.9),(741.9,369.5),116.0475,108.2756,11.84,480,480,'range'); print('eagle-chord f',round(fe,1))
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/camB_boat.npy',np.array([*p1,*p2]))
