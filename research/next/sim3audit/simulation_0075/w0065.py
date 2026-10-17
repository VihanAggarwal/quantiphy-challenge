import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0075')
from calib import inter
L=np.load('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0075/lines0065.npy',allow_pickle=True).item()
cx,cy=1080.,540.
VP1=np.mean([inter(L[a],L[b]) for a in ['Lnear','Lfar'] for b in ['Rfar','Rnear']],axis=0)
print('VP1',VP1)
def camera(f, vp=VP1):
    # zero roll; road direction d = K^-1 vp; pitch from d (road horizontal)
    d=np.array([(vp[0]-cx)/f,(vp[1]-cy)/f,1.]); d/=np.linalg.norm(d)
    # world up vector u (in camera coords, y down) must be orthogonal to d and to camera x-axis component? zero roll: up has no x component
    # up = (0, -cos t, -sin t) orthogonal to d: -cos t*d1 - sin t*d2 = 0 -> tan t = -d1/d2
    t=np.arctan2(-d[1],d[2]); up=np.array([0,-np.cos(t),-np.sin(t)])
    # sign: up should point to negative y (image up) mostly
    if up[1]>0: up=-up
    return d,up
def ground(p,f,H,up):
    r=np.array([(p[0]-cx)/f,(p[1]-cy)/f,1.])
    lam=-H/(r@up)   # point X=lam r with X.up = -H
    return lam*r
def line_ground(l,f,H,up):
    # two image points on line l -> ground points
    a,b,c=l
    pts=[]
    for v in (600.,1000.):
        u=-(b*v+c)/a; pts.append(ground((u,v),f,H,up))
    return pts
b14=(885.,537.2); b38=(872.,416.5)
for f in [1600,2000,2060,2120,2156,2180,2200,2400,3000]:
    d,up=camera(f)
    G1=ground(b14,f,1,up); G2=ground(b38,f,1,up)
    disp=np.linalg.norm(G2-G1); H=5.33/disp
    # road width: distance between the left and right curb lines (ground), perpendicular to the road direction d
    side=np.cross(d,up); side/=np.linalg.norm(side)
    def off(l):
        P=line_ground(l,f,H,up); return np.mean([p@side for p in P])
    W1=abs(off(L['Rnear'])-off(L['Lnear'])); W2=abs(off(L['Rfar'])-off(L['Lfar']))
    # bike range at f14 (rear contact, then +0.5 m along road)
    G1m=ground(b14,f,H,up); R14=np.linalg.norm(G1m+0.5*d); G2m=ground(b38,f,H,up); R38=np.linalg.norm(G2m+0.5*d)
    pitch=np.degrees(np.arcsin(-d@up)) 
    print('f %d H %.3f W_near %.2f W_far %.2f  bike range f14 %.2f (given 25.34) f38 %.2f (30.43) along-road dot %.3f'%(f,H,W1,W2,R14,R38,((G2-G1)/disp)@d))
