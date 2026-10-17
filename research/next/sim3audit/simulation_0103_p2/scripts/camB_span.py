import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from geom import *; from reg import *
b=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/camB_boat.npy')
fr=frames('simulation_0023_segmented')
stack=np.stack([fr[i].astype(np.float32) for i in sorted(fr)]); bg=np.median(stack,0)
for fB in [3390,3440,3493]:
  for pB in [0.0,3.0,6.0]:
    # pitch unknown: estimate from boat level motion
    RB=Reg(fB,480,480,pB,(b[0],b[1]),(b[2],b[3]),103.1570,106.0906)
    E1=RB.obj_W((471.1,372.9),116.0475); E2=RB.obj_W((741.9,369.5),108.2756)
    v=E2-E1
    a=RB.project_W(E1-np.array([0,0.5,0])); c=RB.project_W(E1+np.array([0,0.5,0]))
    pxm=np.linalg.norm(c-a); d=(c-a)/pxm
    print('fB',fB,'pB',pB,'boat vz %.2f'%RB.boat_dz,'eagle v W',np.round(v,2),'|v| %.2f'%np.linalg.norm(v),'Y px/m %.2f dir'%pxm,np.round(d,3))
# per-frame eagle extent along projected Y axis, and px/m at that frame (interpolate eagle position linearly in W)
RB=Reg(3440,480,480,1.0,(b[0],b[1]),(b[2],b[3]),103.1570,106.0906)
E1=RB.obj_W((471.1,372.9),116.0475); E2=RB.obj_W((741.9,369.5),108.2756)
out=[]
for i in range(0,75):
    t=i/24.0; E=E1+(E2-E1)*(t-1.0)
    uv=RB.project_W(E)
    a=RB.project_W(E-np.array([0,0.5,0])); c=RB.project_W(E+np.array([0,0.5,0])); pxm=np.linalg.norm(c-a); d=(c-a)/pxm
    x0,y0=int(uv[0])-40,int(uv[1])-40
    if x0<0 or x0+80>960: continue
    diff=np.abs(stack[i]-bg).sum(2)[y0:y0+80,x0:x0+80]
    m=(diff>60).astype(np.uint8)
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); c0=cen[k]; keep=np.zeros_like(m,bool)
    for kk in range(1,n):
        if st[kk,4]>=2 and np.hypot(*(cen[kk]-c0))<30: keep|=(l==kk)
    ys,xs=np.where(keep); pw=xs*d[0]+ys*d[1]; ext=pw.max()-pw.min()+1
    out.append((i,ext,pxm,ext/pxm,keep.sum(),ys.max()-ys.min()+1))
O=np.array(out)
print('frame ext_px px/m span_m area vext')
for r in O: print('%d %.0f %.2f %.2f %d %d'%tuple(r))
print('max span_m %.2f ; top5 mean %.2f'%(O[:,3].max(),np.sort(O[:,3])[-5:].mean()))
