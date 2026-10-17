# Project hypothesised letter corners (desk uv) into the A3 image and draw them, to test visibility vs occlusion by the gun.
import numpy as np, cv2
from a3cam import *
f=2650.; th,M=setup(f)
hN=-3.593*ray(*N,f,M)[2]; hR=-5.009*ray(*R,f,M)[2]; h=(hN+hR)/2
P={k:onplane(*p,f,M,h) for k,p in dict(N=N,R=R,L=L,F=F).items()}
ex=(P['R']-P['N'])/np.linalg.norm(P['R']-P['N']); ey=(P['L']-P['N'])/np.linalg.norm(P['L']-P['N'])
def proj(Xw):
    c=M.T@Xw; return np.array([CX+f*c[0]/c[2], CY+f*c[1]/c[2]])
def uv2img(u,v,z=0): return proj(P['N']+u*ex+v*ey+np.array([0,0,z]))
def uv(p): q=onplane(*p,f,M,h)-P['N']; return np.array([q@ex,q@ey])
Lc=uv((1320.,624.5)); Nc=uv((1362.,643.5))
u0=(Lc[0]+Nc[0])/2; vN=Nc[1]; vF=Lc[1]
print('letter left edge u0 %.3f, near v %.3f far v %.3f'%(u0,vN,vF))
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0209.mp4'); ok,im=cap.read()
x0,y0,x1,y1,sc=1290,590,1560,665,4
c=cv2.resize(im[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
cols={0.20:(0,255,255),0.25:(0,255,0),0.27:(255,0,255),0.29:(0,0,255)}
for Lgt,col in cols.items():
    pts=[uv2img(u0,vN),uv2img(u0+Lgt,vN),uv2img(u0+Lgt,vF),uv2img(u0,vF)]
    print('length %.2f: near-right corner img %s  far-right corner img %s'%(Lgt,pts[1].round(1),pts[2].round(1)))
    q=[(int((p[0]-x0)*sc),int((p[1]-y0)*sc)) for p in pts]
    for i in range(4): cv2.line(c,q[i],q[(i+1)%4],col,1)
cv2.imwrite('frames/a3_letter_hyp.png',c)
# 3cm-tall grip occlusion: how far behind (in v) does a 3 cm tall object hide the table?
for z in (0.02,0.03,0.04):
    a=uv2img(1.68,0.45,z); b=onplane(*a,f,M,h)-P['N']; print('point at u1.68 v0.45 z%.2f hides table up to v=%.3f'%(z,b@ey))
