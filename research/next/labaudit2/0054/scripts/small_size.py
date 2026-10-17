from common import *
from tracks import *
from fit_a import fit, model, gd
from comps import comps
def costh(u,v): return 1/np.sqrt(1+((u-CX)**2+(v-CY)**2)/F**2)
def blob_minor(v,k,xy,rad=40):
    out,lab=comps(v,k,minA=50,maxA=6000)
    best=None
    for o in out:
        dd=np.hypot(o['x']-xy[0],o['y']-xy[1])
        if dd<12 and (best is None or dd<best[0]): best=(dd,o)
    if best is None: return None
    o=best[1]; ys,xs=np.nonzero(lab==o['i'])
    pts=np.stack([xs,ys],1).astype(np.float32); hull=cv2.convexHull(pts)
    (ex,ey),(a1,a2),ang=cv2.fitEllipse(hull)
    # robust minor: width of mask perpendicular to major axis (90th pct of projected extent)
    th=np.radians(ang); n=np.array([np.cos(th),np.sin(th)])  # fitEllipse angle: first axis direction
    ax1=np.array([np.cos(th),np.sin(th)]); ax2=np.array([-np.sin(th),np.cos(th)])
    p=pts-pts.mean(0); e1=np.ptp(p@ax1)+1; e2=np.ptp(p@ax2)+1
    return min(a1,a2), min(e1,e2), max(e1,e2), o['A']
res={}
for cam,vv,trW,trG,ksW,ksG,g in [('a','ax',A_W,A_G_ax,list(range(24,38)),list(range(25,37)),gd(0)),('b','bx',B_W,B_G,list(range(24,39)),list(range(24,37)),np.load(OUT+'/b_down.npy'))]:
    pW,_=fit(trW,ksW,g); pG,_=fit(trG if cam=='b' else A_G_raw,ksG if cam=='b' else list(range(24,37)),g)
    for name,tr,p in [('W',trW,pW),('G',trG,pG)]:
        for k in sorted(tr):
            if k<25 or k>35: continue
            m=blob_minor(vv,k,tr[k])
            if m is None: continue
            C=model(p,np.array([tcap(k)]),1.0,g)[0]; r=np.linalg.norm(C)
            D_ell=m[0]*r*costh(*tr[k])/F; D_ext=m[1]*r*costh(*tr[k])/F
            res.setdefault((cam,name),[]).append((k,D_ell,D_ext))
            print(cam,name,k,'minor_ell=%.1f minor_ext=%.1f major=%.1f r=%.3f D_ell=%.4f D_ext=%.4f'%(m[0],m[1],m[2],r,D_ell,D_ext))
for key,L in res.items():
    a=np.array(L); print(key,'median D_ell=%.4f D_ext=%.4f n=%d'%(np.median(a[:,1]),np.median(a[:,2]),len(a)))
for cam in 'ab':
    W=dict((k,(d1,d2)) for k,d1,d2 in res[(cam,'W')]); G=dict((k,(d1,d2)) for k,d1,d2 in res[(cam,'G')])
    ks=sorted(set(W)&set(G)); r1=[W[k][0]/G[k][0] for k in ks]; r2=[W[k][1]/G[k][1] for k in ks]
    print(cam,'W/G per frame (ell):',' '.join('%.2f'%x for x in r1),' median %.3f'%np.median(r1),' (ext) median %.3f'%np.median(r2))
