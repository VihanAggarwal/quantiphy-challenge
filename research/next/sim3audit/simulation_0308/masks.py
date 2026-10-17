import cv2, numpy as np
def load(c):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{c}.mp4')
    fr=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        fr.append(f)
    return fr
def bgfit(f, mask_bg):
    H,W=f.shape[:2]
    yy,xx=np.mgrid[0:H,0:W]
    x=(xx/W*2-1); y=(yy/H*2-1)
    terms=[np.ones_like(x),x,y,x*x,x*y,y*y,x**3,x*x*y,x*y*y,y**3]
    A=np.stack([t[mask_bg] for t in terms],1)
    out=np.zeros_like(f,dtype=np.float32)
    for ch in range(3):
        c,*_=np.linalg.lstsq(A,f[...,ch][mask_bg].astype(np.float64),rcond=None)
        out[...,ch]=sum(ci*t for ci,t in zip(c,terms))
    return out
def mask(f):
    g=f.mean(2)
    bg0=g>140
    sub=np.zeros_like(bg0); sub[::4,::4]=True
    B=bgfit(f, bg0&sub)
    d=np.linalg.norm(f.astype(np.float32)-B,axis=2)
    m=(d>18).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    m=(lab==k).astype(np.uint8)
    # fill holes
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    mm=np.zeros_like(m); cv2.drawContours(mm,cnts,-1,1,-1)
    return mm,d
if __name__=='__main__':
    fr=load('0304')
    np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/dummy.npy',np.zeros(1))
    for i in (0,24,48,71):
        m,d=mask(fr[i])
        vis=fr[i].copy(); cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(vis,cnts,-1,(0,0,255),3)
        cv2.imwrite(f'frames/mask_{i:02d}.png',cv2.resize(vis,(1280,720)))
        ys,xs=np.nonzero(m); print(i,m.sum(),xs.min(),xs.max(),ys.min(),ys.max())
