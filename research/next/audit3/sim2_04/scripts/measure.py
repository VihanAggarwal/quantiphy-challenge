import cv2, numpy as np, sys, os
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_04/scripts')
from track import read_all, build_bg
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_04/'
i=int(sys.argv[1]); mode=sys.argv[2]
F=read_all(i)
bg,_=build_bg(F)
rows=[]
for n,f in enumerate(F):
    d=np.abs(f.astype(np.int16)-bg.astype(np.int16)).max(2)
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    if mode=='dark100': m=(g<100)&(d>20)
    elif mode=='dark110': m=(g<110)&(d>20)
    elif mode.startswith('diff'):
        thr=int(mode[4:].split('y')[0]); m=d>thr
        if 'y' in mode: m[int(mode.split('y')[1]):]=False
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nlab,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if nlab<=1: rows.append([n]+[np.nan]*6); continue
    big=np.argmax(st[1:,4])+1; bx,by,bw,bh,ba=st[big]
    keep=np.zeros(nlab,bool)
    for k in range(1,nlab):
        x,y,w,h,a=st[k]
        if a>=40 and x<bx+bw+40 and x+w>bx-40 and y<by+bh+40 and y+h>by-40: keep[k]=True
    mm=keep[lab]
    ys,xs=np.nonzero(mm)
    rows.append([n,xs.min(),xs.max(),ys.min(),ys.max(),xs.mean(),ys.mean()])
    if os.environ.get('OVL') and n==int(os.environ['OVL']):
        o=f.copy(); o[mm]=(0.5*o[mm]+[0,0,127]).astype(np.uint8)
        x0,x1,y0,y1=max(xs.min()-60,0),min(xs.max()+60,2560),max(ys.min()-60,0),min(ys.max()+60,1440)
        cv2.imwrite(W+f'ovl_{i}.png',cv2.resize(o[y0:y1,x0:x1],None,fx=0.6,fy=0.6))
r=np.array(rows,float)
np.savetxt(W+f'trk_{i}.txt',r,fmt='%.2f')
for q in r[::int(os.environ.get('STEP','6'))]:
    print('f%2d x[%5.0f,%5.0f] w=%4.0f y[%4.0f,%4.0f] h=%4.0f cx=%.1f'%(q[0],q[1],q[2],q[2]-q[1]+1,q[3],q[4],q[4]-q[3]+1,q[5]))
