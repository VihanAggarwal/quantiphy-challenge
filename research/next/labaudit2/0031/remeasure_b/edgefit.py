import cv2, numpy as np, json, sys
vid = sys.argv[1] if len(sys.argv)>1 else ''
tag = vid or 'a'
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0031%s.mp4'%vid)
F=[]
while True:
    ok,x=c.read()
    if not ok: break
    F.append(x)
init=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/tracka.json'))
def fit_circle(x,y):
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
    s=np.linalg.lstsq(A,b,rcond=None)[0]
    cx,cy=s[0],s[1]; return cx,cy,np.sqrt(s[2]+cx*cx+cy*cy)
def edge_fit(score, cx, cy, r0, angs):
    pts=[]
    for a in angs:
        d=np.array([np.cos(a),np.sin(a)])
        ts=np.arange(0.4*r0, 1.6*r0, 0.25)
        xs=(cx+ts*d[0]).astype(np.float32); ys=(cy+ts*d[1]).astype(np.float32)
        prof=cv2.remap(score, xs.reshape(1,-1), ys.reshape(1,-1), cv2.INTER_LINEAR)[0]
        prof=cv2.GaussianBlur(prof.reshape(1,-1).astype(np.float32),(5,1),0)[0] if len(prof)>5 else prof
        inside=np.median(prof[:int(len(prof)*0.3)]); outside=np.median(prof[-int(len(prof)*0.2):])
        half=(inside+outside)/2
        # first crossing from inside going out
        k=None
        for j in range(1,len(prof)):
            if (prof[j-1]-half)*(prof[j]-half)<=0 and ts[j]>0.6*r0:
                k=j;break
        if k is None or abs(inside-outside)<15: continue
        tt=ts[k-1]+(half-prof[k-1])/(prof[k]-prof[k-1]+1e-9)*(ts[k]-ts[k-1])
        pts.append((cx+tt*d[0], cy+tt*d[1]))
    pts=np.array(pts)
    if len(pts)<8: return None
    for it in range(3):
        ccx,ccy,rr=fit_circle(pts[:,0],pts[:,1])
        res=np.hypot(pts[:,0]-ccx,pts[:,1]-ccy)-rr
        keep=np.abs(res)<max(1.0,2.5*np.std(res))
        pts=pts[keep]
    ccx,ccy,rr=fit_circle(pts[:,0],pts[:,1])
    return ccx,ccy,rr,len(pts),float(np.std(np.hypot(pts[:,0]-ccx,pts[:,1]-ccy)-rr))
angs=np.deg2rad(np.r_[np.arange(160,381,5)])  # left side, over top, right side (y down => 270 = up)
out=[]
for i,fr in enumerate(F):
    hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV).astype(np.float32)
    rec={'i':i}
    o=init[i]
    if 't_c' in o and i<=42:
        sc=hsv[...,1]*((hsv[...,0]>15)&(hsv[...,0]<45))
        r=edge_fit(sc.astype(np.float32),o['t_c'][0],o['t_c'][1],o['t_req'],angs)
        if r: rec['t']=r
    if 'w_c' in o:
        sc=(hsv[...,2]-hsv[...,1])
        r=edge_fit(sc.astype(np.float32),o['w_c'][0],o['w_c'][1]+1.5,max(o['w_bbox'][2]/2,7),angs)
        if r: rec['w']=r
    out.append(rec)
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/edge_%s.json'%tag,'w'))
for o in out:
    s='%2d'%o['i']
    for k in 't','w':
        if k in o: s+='  %s (%.2f,%.2f) r=%.2f n=%d sd=%.2f'%(k,*o[k])
        else: s+='  %s -'%k
    print(s)
