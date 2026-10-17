"""Ball track on s (red on green), o (red hue) and X (non-white blob, string removed by opening)."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
def blob(m, prev=None):
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: return None
    if prev is None: k=1+np.argmax(st[1:,4])
    else:
        d=np.hypot(cen[1:,0]-prev[0],cen[1:,1]-prev[1]); score=st[1:,4]/(1+d/20.); k=1+np.argmax(score)
    return (lab==k).astype(np.uint8)
def meas(m):
    ys,xs=np.nonzero(m)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea)
    (ex,ey),(a1,a2),ang=cv2.fitEllipse(c)
    (mx,my),rr=cv2.minEnclosingCircle(c)
    x0,y0,w,h=cv2.boundingRect(c)
    return dict(u=float(xs.mean()),v=float(ys.mean()),eu=ex,ev=ey,emin=min(a1,a2),emaj=max(a1,a2),ang=ang,
                bu=x0+w/2-0.5,bv=y0+h/2-0.5,w=w,h=h,area=int(len(xs)),deq=2*np.sqrt(len(xs)/np.pi))
out={}
for r in ['s','','X']:
    fr=frames(r); rows=[]; prev=None
    for i,im in enumerate(fr):
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); h,sa,v=cv2.split(hsv)
        if r=='s': m=(((h<14)|(h>172))&(sa>110)&(v>90)).astype(np.uint8)
        elif r=='': m=(((h<12)|(h>170))&(sa>120)&(v>100)).astype(np.uint8)
        else:
            g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(int)
            m=((255-im.min(axis=2).astype(int))>14).astype(np.uint8)
            m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
        m[680:,:]=0
        if r=='': m[:, :400]=0; m[:, 900:]=0
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
        b=blob(m,prev)
        if b is None: rows.append(None); continue
        d=meas(b); d['f']=i; prev=(d['u'],d['v']); rows.append(d)
    out[r or 'o']=rows
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/track.json','w'),default=float)
for i in range(49):
    if out['X'][i] is None: out['X'][i]=dict(u=np.nan,v=np.nan,emin=np.nan,deq=np.nan)
    s=out['s'][i]; o=out['o'][i]; x=out['X'][i]
    print(f"{i:2d} c{cap(i):2d} s({s['u']:6.1f},{s['v']:6.1f}) e({s['eu']:6.1f},{s['ev']:6.1f}) min{s['emin']:5.1f} maj{s['emaj']:5.1f} w{s['w']} h{s['h']} deq{s['deq']:5.1f} | o({o['u']:6.1f},{o['v']:6.1f}) deq{o['deq']:5.1f} | X({x['u']:6.1f},{x['v']:6.1f}) min{x['emin']:5.1f} deq{x['deq']:5.1f}")
