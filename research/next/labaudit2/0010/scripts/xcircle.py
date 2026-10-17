"""Circle fit to the ball outline: X render (non-white mask, string removed) and s render (redness half-max contour).
Contour points within +-60 deg of the string attachment direction (top) are dropped."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/track.json'))
ST=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/string_s.json'))
def circfit(x,y):
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
    for it in range(3):
        p,*_=np.linalg.lstsq(A,b,rcond=None); cx,cy=p[0],p[1]; r=np.sqrt(p[2]+cx*cx+cy*cy)
        d=np.hypot(x-cx,y-cy)-r; keep=np.abs(d)<2.5*np.std(d)+0.5
        A,b,x,y=A[keep],b[keep],x[keep],y[keep]
    return cx,cy,r,np.std(d)
res=[]
fX=frames('X'); fS=frames('s')
for i in range(49):
    u,v=T['s'][i]['u'],T['s'][i]['v']
    x0,y0=int(u)-45,int(v)-45
    out=dict(f=i)
    for nm,im in (('X',fX[i]),('s',fS[i])):
        c=im[y0:y0+90,x0:x0+90].astype(float)
        if nm=='X':
            m=((255-c.min(axis=2))>14).astype(np.uint8)
        else:
            red=c[:,:,2]-c[:,:,1]; m=(red>45).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
        n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n_<2: continue
        kk=1+np.argmax(st[1:,4]); m=(lab==kk).astype(np.uint8)
        cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cn=max(cnts,key=cv2.contourArea)[:,0,:].astype(float)
        # direction of string at ball: from ball toward pivot
        ang_s=np.arctan2(-(1.0),-(ST[i]['k']))  # string goes up: dy=-1, dx=-k
        mx,my=cn[:,0].mean(),cn[:,1].mean()
        a=np.arctan2(cn[:,1]-my,cn[:,0]-mx)
        da=np.angle(np.exp(1j*(a-ang_s)))
        sel=np.abs(da)>np.radians(40)
        cx,cy,r,sd=circfit(cn[sel,0],cn[sel,1])
        out[nm]=dict(u=cx+x0,v=cy+y0,d=2*r,sd=sd)
    res.append(out)
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/circ.json','w'))
for o in res:
    i=o['f']; X=o.get('X'); s=o.get('s')
    print(f"k{i:2d} c{cap(i):2d} X d={X['d']:5.2f} ({X['u']:6.1f},{X['v']:6.1f}) sd{X['sd']:.2f} | s d={s['d']:5.2f} ({s['u']:6.1f},{s['v']:6.1f}) sd{s['sd']:.2f} | Rc X {F*0.07/X['d']:.3f} s {F*0.07/s['d']:.3f}")
