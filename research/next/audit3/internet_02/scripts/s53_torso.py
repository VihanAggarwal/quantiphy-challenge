# Track the rider's torso/cap (template matching) in internet_0053; static camera.
import cv2, numpy as np
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0053.mp4'
c=cv2.VideoCapture(P); G=[]
while True:
    ok,im=c.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
N=len(G)
def track(tf, box):
    x0,y0,w,h=box; T=G[tf][y0:y0+h,x0:x0+w].copy()
    xs=np.full(N,np.nan); scs=np.zeros(N)
    for i in range(N):
        band=G[i][y0-30:y0+h+30]
        r=cv2.matchTemplate(band,T,cv2.TM_CCOEFF_NORMED)
        _,mx,_,ml=cv2.minMaxLoc(r); x,y=ml
        dx=0
        if 0<x<r.shape[1]-1:
            a,b,cc=r[y,x-1],r[y,x],r[y,x+1]; den=a-2*b+cc; dx=0.5*(a-cc)/den if den!=0 else 0
        xs[i]=x+dx; scs[i]=mx
    return xs,scs
# torso+cap template at f40: person x ~1157..1300 ; cap/torso region x 1170..1260, y 385..520
xa,sa=track(40,(1170,385,90,135))
# legs/pants at f40 y 520..640
xb,sb=track(40,(1180,520,90,120))
for i in range(0,N,5): print(i, round(xa[i],1), round(sa[i],2), round(xb[i],1), round(sb[i],2))
ok=(sa>0.6)
t=np.arange(N)
p=np.polyfit(t[ok],xa[ok],2); print('quad fit torso px/frame at 0,40,80:', np.polyval(np.polyder(p),[0,40,80]))
okb=(sb>0.6); pb=np.polyfit(t[okb],xb[okb],2); print('quad fit legs:', np.polyval(np.polyder(pb),[0,40,80]))
print('valid torso frames', t[ok].min(), t[ok].max(), 'disp', xa[t[ok].max()]-xa[t[ok].min()], 'per frame', (xa[t[ok].max()]-xa[t[ok].min()])/(t[ok].max()-t[ok].min()))
print('legs valid', t[okb].min(), t[okb].max(), (xb[t[okb].max()]-xb[t[okb].min()])/(t[okb].max()-t[okb].min()))
