import cv2, numpy as np, sys, os
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_04/scripts')
from track import read_all, build_bg
i=int(sys.argv[1]); thr=int(sys.argv[2]); sat=int(sys.argv[3]); frs=[int(x) for x in sys.argv[4].split(',')]
ylim=(int(sys.argv[5]),int(sys.argv[6])) if len(sys.argv)>6 else (0,1440)
F=read_all(i); bg,_=build_bg(F)
sb=cv2.cvtColor(bg,cv2.COLOR_BGR2HSV)[...,1].astype(int)
res=[]
for n,f in enumerate(F):
    d=np.abs(f.astype(np.int16)-bg.astype(np.int16)).max(2)
    m=d>thr
    if sat>0:
        s=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)[...,1].astype(int); m&=(s-sb)>sat
    m[:ylim[0]]=False; m[ylim[1]:]=False
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    nl,lab,st,_=cv2.connectedComponentsWithStats(m)
    big=np.argmax(st[1:,4])+1; bx,by,bw,bh,_=st[big]
    keep=np.zeros(nl,bool)
    for k in range(1,nl):
        x,y,w,h,a=st[k]
        if a>=10 and x<bx+bw+30 and x+w>bx-30 and y<by+bh+30 and y+h>by-30: keep[k]=True
    ys,xs=np.nonzero(keep[lab])
    res.append((n,ys.min(),ys.max(),ys.max()-ys.min()+1,xs.min(),xs.max()))
    if os.environ.get('OVL') and n==int(os.environ['OVL']):
        o=f.copy(); mm=keep[lab]; o[mm]=(0.5*o[mm]+[0,0,127]).astype(np.uint8)
        cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_04/yovl_{i}.png',cv2.resize(o[max(ys.min()-40,0):ys.max()+40,max(xs.min()-40,0):xs.max()+40],None,fx=0.5,fy=0.5))
r=np.array(res)
h=r[:,3]
top=np.argsort(-h)[:6]
print(i,'max h frames:',[(int(r[k,0]),int(h[k]),int(r[k,1]),int(r[k,2])) for k in sorted(top)], 'f0 h',h[0],'median',np.median(h))
print(' h per frame:',' '.join(str(int(x)) for x in h))
