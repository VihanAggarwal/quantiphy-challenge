import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
import geo
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
def teal_mask(im):
    b,g,r=[im[...,i].astype(int) for i in range(3)]
    m=((b-r>12)&(g-r>8)&(g>100)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: return None
    k=1+np.argmax(st[1:,4]); return (lab==k), st[k], cen[k]
tag=sys.argv[1] if len(sys.argv)>1 else 'x'
prev=None; rows=[]
for i in range(14,40):
    im=cv2.imread(D+f'frames/{tag}{i:02d}.png')
    res=teal_mask(im)
    if res is None: continue
    m,st,c=res
    # 3D: on slope top face plane (h=1.46) while on slope; on table plane (h=1.46) afterwards
    Xs=on_slope(c[0],c[1],0.0073); Xt=geo.on_plane(c[0],c[1],0.0073)
    sc=slope_coords(Xs)
    rows.append((i,c[0],c[1],st[4],Xs,Xt,sc))
for k,(i,u,v,a,Xs,Xt,sc) in enumerate(rows):
    s=''
    if k+1<len(rows) and rows[k+1][0]==i+1:
        vs=np.linalg.norm(rows[k+1][4]-Xs)*100*24; vt=np.linalg.norm(rows[k+1][5]-Xt)*100*24
        s='fwd speed slope-plane %.0f table-plane %.0f cm/s'%(vs,vt)
    print('n %2d t %.3f c (%.1f,%.1f) area %4d range_slope %.3f along %.1f  %s'%(i,i/24,u,v,a,np.linalg.norm(Xs),sc[1],s))
