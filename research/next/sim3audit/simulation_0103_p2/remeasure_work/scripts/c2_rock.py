import numpy as np
from cam import Cam
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/remeasure_work/'
cnt=np.load(W+'rockcontour_0043_segmented_30.npy').astype(float)
bp1=np.array([360.,925.]); disp=np.array([-85.74,-24.81])
D1,D2=173.7093,174.5515
def run(f,d,dz=0.0,bp=bp1,verbose=False):
    c=Cam(f,d,(540,540))
    P1=c.pt(bp[0],bp[1],D1); P2=c.pt(bp[0]+disp[0],bp[1]+disp[1],D2)
    V=P2-P1; hdg=V[:2]/np.linalg.norm(V[:2])
    h=-P1[2]+dz   # camera height above sand plane; dz = z_origin - z_sand
    G=c.ground(cnt[:,0],cnt[:,1],h)[:,:2]
    a=G@hdg; b=G@np.array([-hdg[1],hdg[0]])
    # also principal axes of footprint
    if verbose:
        print('V',np.round(V,3),'|V|',round(np.linalg.norm(V),3),'h',round(h,2),'hdg',np.round(hdg,3))
    # oriented min/max over angles
    angs=np.radians(np.arange(0,180,1)); ext=[]
    for t in angs:
        u=np.array([np.cos(t),np.sin(t)]); p=G@u; ext.append(p.max()-p.min())
    ext=np.array(ext)
    return a.max()-a.min(), b.max()-b.min(), ext.max(), ext.min(), np.degrees(angs[ext.argmax()]), np.degrees(np.arctan2(hdg[1],hdg[0]))
for f in [3790,3860,3950]:
    for d in [53.2,54.5,56]:
        r=run(f,d)
        print(f,d,'along hdg %.2f  perp %.2f  maxext %.2f minext %.2f at %.0f deg (hdg %.1f)'%r)
run(3860,54.5,verbose=True)
for dz in [-2,2,4]:
    print('dz',dz,'%.2f %.2f'%run(3860,54.5,dz)[:2])
