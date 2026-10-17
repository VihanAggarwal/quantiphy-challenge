# Route 3: use the gun as a ruler shared by both cameras.
# A3 (this clip's camera, scale from its own depth_info ranges): letter left edge u, barrel-tip u, grip-end u on the desk long axis.
# A2 (frontal level camera, 0208/0204): x positions of letter ends, barrel tip, grip end -> metric offsets via X=(x-xv)*h/(y-yh).
# Ratio form (independent of h): letter_len = (A3 gun u-extent) * (A2 letter extent / A2 gun u-extent).
import numpy as np
from a3cam import *
res=[]
for f in (2630.,2650.,2670.):
    th,M=setup(f)
    hN=-3.593*ray(*N,f,M)[2]; hR=-5.009*ray(*R,f,M)[2]; h=(hN+hR)/2
    P={k:onplane(*p,f,M,h) for k,p in dict(N=N,R=R,L=L,F=F).items()}
    ex=(P['R']-P['N'])/np.linalg.norm(P['R']-P['N']); ey=(P['L']-P['N'])/np.linalg.norm(P['L']-P['N'])
    def uv(p,z=0.0): q=onplane(*p,f,M,h-z)-P['N']; return np.array([q@ex,q@ey])
    for zb in (0.005,0.012):
        tip=uv((1353.,621.5),zb)      # barrel tip, lowest point (elevated zb above table)
        grip=uv((1504.,643.),0.0)     # grip end, bottom corner on the table
        Lft=uv((1320.,624.5))         # letter left (far) corner
        Nc=uv((1362.,643.5))          # letter near-left corner
        gun_u=grip[0]-tip[0]
        res.append((f,zb,gun_u,tip[0]-Nc[0]))
        print('f=%.0f zb=%.3f  tip uv %s grip uv %s  letter-left-edge u %.3f  gun u-extent %.3f  tip-minus-letteredge %.3f'%(f,zb,tip.round(3),grip.round(3),(Lft[0]+Nc[0])/2,gun_u,tip[0]-(Lft[0]+Nc[0])/2))
# A2 frontal measurements (0208 frame 0, gridded crop): pixels
xv,yh2=1060.0,540.0
letL,letR,yL=1191.4,1389.0,1001.0
tipx,gripx=1216.4,1365.0
print()
for ytip,ygrip in [(985,1005),(990,1010),(995,1012)]:
    # metric x in units of h
    XL=(letL-xv)/(yL-yh2); XR=(letR-xv)/(yL-yh2); Xt=(tipx-xv)/(ytip-yh2); Xg=(gripx-xv)/(ygrip-yh2)
    ratio=(XR-XL)/(Xg-Xt)
    print('A2 contact rows tip %d grip %d: letter/gun-u ratio %.3f  (tip - letter left)/letter %.3f'%(ytip,ygrip,ratio,(Xt-XL)/(XR-XL)))
    for f,zb,gu,_ in res:
        print('    f=%.0f zb=%.3f -> letter length %.3f'%(f,zb,ratio*gu))
