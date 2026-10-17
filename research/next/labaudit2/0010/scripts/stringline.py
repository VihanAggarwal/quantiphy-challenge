"""String (grey, low saturation on green) in the s render: top endpoint and line direction per frame."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/track.json'))
fr=frames('s'); out=[]
for i,im in enumerate(fr):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); h,s,v=cv2.split(hsv)
    g=im[:,:,1].astype(int); r=im[:,:,2].astype(int); b=im[:,:,0].astype(int)
    m=((s<90)&(v>60)).astype(np.uint8)   # grey string, not green bg
    m[:150]=0; m[460:]=0; m[:, :560]=0; m[:, 760:]=0
    u,vv=T['s'][i]['u'],T['s'][i]['v']
    ys,xs=np.nonzero(m)
    keep=ys<vv-5
    ys,xs=ys[keep],xs[keep]
    if len(ys)<10: out.append(None); continue
    A=np.c_[ys,np.ones_like(ys)]; k,c=np.linalg.lstsq(A,xs,rcond=None)[0]
    res=xs-(k*ys+c); good=np.abs(res)<3
    k,c=np.linalg.lstsq(A[good],xs[good],rcond=None)[0]
    yt=np.percentile(ys[good],1)
    out.append(dict(f=i,ytop=float(yt),xtop=float(k*yt+c),k=float(k),c=float(c),n=int(good.sum())))
    print(f"{i:2d} top=({k*yt+c:6.1f},{yt:6.1f}) slope dx/dy={k:+.3f} n={good.sum()} ball=({u:.1f},{vv:.1f}) line-at-ball x={k*vv+c:.1f}")
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/string_s.json','w'))
