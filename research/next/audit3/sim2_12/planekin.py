import cv2, numpy as np, sys
res={}
for v in ('0229','0230'):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4'); fr=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
    bg=np.median(np.stack(fr[36:]+fr[1:12]),axis=0)
    P={}
    for i in range(16,33):
        d=fr[i]-bg; m=(d>25).astype(np.uint8); m[750:]=0; m[:250]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        # weighted centroid and bbox centre
        P[i]=(cen[k][0],cen[k][1],x+w/2,y+h/2)
    t=np.array(sorted(P)); X=np.array([P[i][0] for i in t]); Y=np.array([P[i][1] for i in t])
    Xb=np.array([P[i][2] for i in t]); Yb=np.array([P[i][3] for i in t])
    for lab_,XX,YY in (('centroid',X,Y),('bboxc',Xb,Yb)):
        sp=np.hypot(np.diff(XX),np.diff(YY)); ts=t[1:]   # backward diff speed at frame ts
        # raw at 24 and 30
        raw24=sp[ts==24][0]; raw30=sp[ts==30][0]
        # smoothed: fit cubic to positions then backward diff
        px=np.polyfit(t,XX,3); py=np.polyfit(t,YY,3)
        def v(k): return np.hypot(np.polyval(px,k)-np.polyval(px,k-1),np.polyval(py,k)-np.polyval(py,k-1))
        # accel: local linear fit of raw speed series over +-3 frames
        def acc(k):
            sel=(ts>=k-3)&(ts<=k+3); c=np.polyfit(ts[sel],sp[sel],1); return c[0]*576
        def vfit(k):
            sel=(ts>=k-3)&(ts<=k+3); c=np.polyfit(ts[sel],sp[sel],1); return np.polyval(c,k)
        print(v,lab_,'v24 raw %.2f cubic %.2f lin %.2f | v30 raw %.2f cubic %.2f lin %.2f px/f | a24 %.0f a30 %.0f px/s2 | cubic a24 %.0f a30 %.0f'%(raw24,v(24),vfit(24),raw30,v(30),vfit(30),acc(24),acc(30),(v(24.5)-v(23.5))*576,(v(30.5)-v(29.5))*576))
