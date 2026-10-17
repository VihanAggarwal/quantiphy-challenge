# basketball displacement 0.4 s -> 0.9 s in take b: rest point (cap 10) to the 0.9 s point (stated 2.7777)
import labelstyle as L
from geom import *
tr=load_tr('b')['bb']
rest=[tr[k] for k in range(0,11)]
ur=np.mean([d['cx'] for d in rest]); vr=np.mean([d['cy'] for d in rest]); dr=np.mean([d['deq'] for d in rest])
print('rest pixel (%.1f,%.1f) deq %.1f'%(ur,vr,dr))
for f in [711,763,777]:
    M=L.Model('b',f,1.5)
    # 0.9 s label point
    P09=[M.label_point('bb',c,'P',22.5) for c in [22,23]]
    u9=[M.pix('bb',c) for c in [22,23]]
    P09=[2.7777*ray(u,v,f) for u,v in u9]
    # rest range: plane route (surface) ; size route scaled by the 0.9 s label (as the label scale) ; size with camera-a K
    rp=np.linalg.norm(plane_point(ur,vr,M.n,M.h,0.116,f))-0.116
    k,_=M.scale('bb','S',22.5)
    rs=k/((dr+1.5)*cosa(ur,vr,f)**1.5)-0.116
    Ka=(2.27+0.116)*(76.4+1.5)*cosa(737.3,535.1,f)**1.5   # camera a calibration, same masks
    rsa=Ka/((dr+1.5)*cosa(ur,vr,f)**1.5)-0.116
    floor=np.linalg.norm(plane_point(ur,vr,M.n,M.h,0.0,f))
    for nm,r0 in [('plane',rp),('size(b label scale)',rs),('size(camera-a K)',rsa),('floor behind',floor)]:
        P0=r0*ray(ur,vr,f)
        D=[100*np.linalg.norm(P-P0) for P in P09]
        print(f'f={f} {nm:22s} rest surface range {r0:.3f}  disp to cap22 {D[0]:.1f} cap23 {D[1]:.1f} mean {np.mean(D):.1f}')
