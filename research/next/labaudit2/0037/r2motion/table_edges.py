import cv2,numpy as np
def frame0(sfx):
    c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0037%s.mp4'%sfx)
    ok,f=c.read(); return f
f=frame0('s')
hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
# brown: hue 5-25, sat>60
br=(hsv[...,0]>=5)&(hsv[...,0]<=25)&(hsv[...,1]>50)&(hsv[...,2]>60)
top={}
for x in range(200,1145):
    col=br[400:640,x]
    # find first run of >=6 brown pixels
    run=0
    for y in range(len(col)):
        run=run+1 if col[y] else 0
        if run>=6:
            top[x]=400+y-5; break
xs=np.array(sorted(top)); ys=np.array([top[x] for x in xs])
def fitline(sel):
    A=np.c_[xs[sel],np.ones(sel.sum())]; p,res,_,_=np.linalg.lstsq(A,ys[sel],rcond=None)
    r=ys[sel]-A@p
    return p, np.abs(r).max()
for name,(a,b) in dict(left=(215,425),far=(500,520),far2=(610,650),far3=(820,900),right=(925,1130)).items():
    sel=(xs>=a)&(xs<=b)
    p,e=fitline(sel); print(name,p,e)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/top.npy',np.c_[xs,ys])
for x in range(200,1145,25): print(x,top.get(x))
