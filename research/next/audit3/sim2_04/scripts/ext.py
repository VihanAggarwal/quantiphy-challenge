import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_04/scripts')
from track import read_all, build_bg
i=int(sys.argv[1]); frs=[int(x) for x in sys.argv[2].split(',')]
ymax=int(sys.argv[3]) if len(sys.argv)>3 and sys.argv[3]!='-' else 99999
F=read_all(i); bg,split=build_bg(F)
for fr in frs:
    f=F[fr]
    d=np.abs(f.astype(np.int16)-bg.astype(np.int16)).max(2)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV); s=hsv[...,1].astype(int)
    sb=cv2.cvtColor(bg,cv2.COLOR_BGR2HSV)[...,1].astype(int)
    out=[]
    for thr,sthr in [(40,None),(25,None),(15,None),(25,30),(15,25)]:
        m=d>thr
        if sthr is not None: m&=(s-sb)>sthr
        m[ymax:]=False
        m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))>0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
        big=np.argmax(st[1:,4])+1; bx,by,bw,bh,_=st[big]
        keep=np.zeros(n,bool)
        for k in range(1,n):
            x,y,w,h,a=st[k]
            if a>=15 and x<bx+bw+60 and x+w>bx-60 and y<by+bh+60 and y+h>by-60: keep[k]=True
        mm=keep[lab]
        ys,xs=np.nonzero(mm)
        out.append(f'thr{thr}/s{sthr}: x[{xs.min()},{xs.max()}] w={xs.max()-xs.min()+1} y[{ys.min()},{ys.max()}] h={ys.max()-ys.min()+1}')
    print(fr,' | '.join(out))
