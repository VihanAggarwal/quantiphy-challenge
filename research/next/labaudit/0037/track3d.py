"""Ping-pong ball 3D track for captured_0037 (all renders). Two depth routes:
 A: apparent size (fitted-ellipse minor axis) scaled to the stated range 1.055 m at t=1.0 s (frame 24)
 B: absolute size: Z = f * 0.04 / minor_axis (no stated depth)
 C: bounce frames: ball centre 2 cm above the table plane (plane from table.py), gives Z at bounces only."""
import cv2, numpy as np, sys
F=711.0; CX,CY=640.,360.
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0037/plane.npy')
def track(v):
    fr=[cv2.imread('frames/v%s_%02d.png'%(v,i)) for i in range(49)]
    med=np.median(np.stack(fr[::2]),axis=0).astype(np.float32)
    rows=[]
    for i,f in enumerate(fr):
        d=np.abs(f.astype(np.float32)-med).sum(2)
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        m=((d>60)&(hsv[...,2]>140)&(hsv[...,1]<80)).astype(np.uint8)
        m[:200]=0; m[600:]=0; m[:,1000:]=0
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        if not cs: rows.append([i,np.nan]*1+[np.nan]*4); continue
        c=max(cs,key=cv2.contourArea)
        (x,y),(a,b),ang=cv2.fitEllipse(c)
        rows.append([i,x,y,min(a,b),max(a,b)])
    return np.array(rows,float)
def P(u,v,Z): return np.array([(u-CX)/F*Z,(v-CY)/F*Z,Z])
if __name__=='__main__':
    for v in sys.argv[1:] or ['x']:
        T=track(v)
        mi=T[:,3]
        # smooth minor axis in time with a robust local fit (frames 12..48)
        idx=np.arange(12,49)
        p=np.polyfit(idx,mi[idx],2)
        ms=np.polyval(p,np.arange(49))
        r24=np.linalg.norm([(T[24,1]-CX)/F,(T[24,2]-CY)/F,1]); Z24=1.055/r24
        kA=Z24*ms[24]
        print(v,'minor@24 raw %.1f smooth %.1f  Z24(stated)=%.3f  Z24(4cm)=%.3f'%(mi[24],ms[24],Z24,F*0.04/ms[24]))
        X={}
        for name,k in (('A',kA),('B',F*0.04)):
            X[name]=np.array([P(T[i,1],T[i,2],k/ms[i]) for i in range(49)])
        for i in range(10,49):
            print('%2d u=%6.1f v=%6.1f minor=%5.1f(sm %5.1f) major=%5.1f ZA=%.3f ZB=%.3f hA=%.3f'%(i,T[i,1],T[i,2],T[i,3],ms[i],T[i,4],X['A'][i,2],X['B'][i,2], 0.172+n@X['A'][i]))
        np.save('trk_%s.npy'%v,T)
