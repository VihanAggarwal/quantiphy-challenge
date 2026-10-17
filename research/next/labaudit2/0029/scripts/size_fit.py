# sub-pixel ball diameter from half-level edges of a yellowness channel along radial rays (upper arc against the
# whiteboard only), circle fit; o render and s render (same footage) as two measurements
import cv2, numpy as np, json
from frames import frames
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
def yell(img):
    b,g,r=[img[...,i].astype(np.float32) for i in range(3)]
    return (r+g)/2-b
def fitcircle(P):
    A=np.c_[2*P[:,0],2*P[:,1],np.ones(len(P))]; b=(P**2).sum(1)
    s=np.linalg.lstsq(A,b,rcond=None)[0]; return s[0],s[1],np.sqrt(s[2]+s[0]**2+s[1]**2)
def measure(img,cx,cy,R0,angs):
    Y=cv2.GaussianBlur(yell(img),(0,0),0.7)
    pts=[]
    for a in angs:
        d=np.array([np.cos(a),np.sin(a)])
        rs=np.arange(0.2*R0,1.9*R0,0.1)
        xs=(cx+rs*d[0]).astype(np.float32); ys=(cy+rs*d[1]).astype(np.float32)
        v=cv2.remap(Y,xs[None],ys[None],cv2.INTER_LINEAR)[0]
        vin=np.median(v[(rs>0.3*R0)&(rs<0.6*R0)]); vout=np.median(v[(rs>1.4*R0)&(rs<1.8*R0)])
        if vin-vout<60: continue
        thr=(vin+vout)/2
        # first crossing going outward from 0.6 R0
        i0=np.searchsorted(rs,0.6*R0)
        idx=np.where(v[i0:]<thr)[0]
        if len(idx)==0: continue
        j=i0+idx[0]
        rr=rs[j-1]+(v[j-1]-thr)/(v[j-1]-v[j])*(rs[j]-rs[j-1])
        pts.append((cx+rr*d[0],cy+rr*d[1]))
    if len(pts)<10: return None
    P=np.array(pts)
    for it in range(2):
        a,b,r=fitcircle(P); res=np.hypot(P[:,0]-a,P[:,1]-b)-r
        keep=np.abs(res)<max(2.5*np.std(res),0.5); P=P[keep]
    a,b,r=fitcircle(P); res=np.hypot(P[:,0]-a,P[:,1]-b)-r
    return a,b,2*r,len(P),float(np.std(res))
out={}
angs=np.deg2rad(np.arange(-200,21,4))   # upper arc (y down): from left-below-horizontal over the top to right-below
for rend in ['','s']:
    F=frames(rend); res={}
    for k in range(20,49):
        t=T['x'][k]; cx,cy=t['cx'],t['cy']; R0=t['ell'][2]/2
        m=measure(F[k],cx,cy,R0,angs)
        if m: res[k]=m
    out[rend or 'o']=res
json.dump({r:{k:list(v) for k,v in d.items()} for r,d in out.items()},open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/sizefit.json','w'))
f=711.
for k in range(20,49):
    s=[]
    for r in ['o','s']:
        m=out[r].get(k)
        s.append('D=%.2f n=%d rms=%.2f R=%.3f'%(m[2],m[3],m[4],f*0.067/m[2]) if m else '-')
    print(k,' | '.join(s))
