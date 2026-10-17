# Ball track on x (green-screen) render: matte components, centroid + moment ellipse.
import cv2, numpy as np, json, sys
FR='/home/user/quantiphy-challenge/research/next/labaudit/0016/frames/f%s_%02d.png'
rend=sys.argv[1] if len(sys.argv)>1 else 'x'
def mask_x(im):
    b,g,r=[im[...,i].astype(int) for i in range(3)]
    m=~((g>150)&(g>r+60)&(g>b+60))
    m=m.astype(np.uint8); m[680:,1000:]=0
    return m
out={}
for i in range(26,46):
    im=cv2.imread(FR%(rend,i))
    m=mask_x(im)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    comps=[]
    for k in range(1,n):
        a=st[k,4]
        if a<800: continue
        x,y,w,h=st[k,:4]
        ys,xs=np.nonzero(lab==k)
        mu=np.cov(np.vstack([xs,ys]))
        ev,evec=np.linalg.eigh(mu)
        maj=4*np.sqrt(ev[1]); mnr=4*np.sqrt(ev[0])
        ang=np.degrees(np.arctan2(evec[1,1],evec[0,1]))
        comps.append(dict(k=int(k),a=int(a),bbox=[int(x),int(y),int(w),int(h)],c=[float(xs.mean()),float(ys.mean())],maj=float(maj),mnr=float(mnr),ang=float(ang)))
    comps.sort(key=lambda c:-c['a'])
    print(i,[(c['a'],c['bbox'],[round(v,1) for v in c['c']],round(c['maj'],1),round(c['mnr'],1),round(c['ang'])) for c in comps[:4]])
