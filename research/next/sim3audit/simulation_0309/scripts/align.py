# Compare dragon position/size in 0302 vs 0309 (content cropped at x 160:2720) via masked template matching
import cv2, numpy as np
bg=np.load('bg0302.npy').astype(np.float32)
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4'); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
A=frames('0302'); B=frames('0309')
print(B[0].shape, 'black bar check', B[10][:, :160].mean(), B[10][:, 2720:].mean(), B[10][:,160:170].mean())
for i in [1,12,24,36,48,60,71]:
    f=A[i]; d=np.abs(f.astype(np.float32)-bg).sum(2); m=(d>40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); x,y,w,h,_=st[k]
    tpl=A[i][y:y+h,x:x+w]; msk=((lab==k)[y:y+h,x:x+w]*255).astype(np.uint8)
    msk3=cv2.merge([msk,msk,msk])
    best=None
    for sc in [0.97,0.98,0.99,1.0,1.01,1.02,1.03]:
        t2=cv2.resize(tpl,None,fx=sc,fy=sc); m2=cv2.resize(msk3,None,fx=sc,fy=sc)
        R=cv2.matchTemplate(B[i],t2,cv2.TM_CCORR_NORMED,mask=m2)
        _,mv,_,ml=cv2.minMaxLoc(R)
        if best is None or mv>best[0]: best=(mv,sc,ml)
    mv,sc,ml=best
    print(i,'0302 bbox',(x,y,w,h),'-> 0309 match at',ml,'dx',ml[0]-x-160,'dy',ml[1]-y,'scale',sc,'score %.3f'%mv)
