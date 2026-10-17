import cv2, numpy as np, sys, json
c=sys.argv[1]; thr=float(sys.argv[2]); y0,y1=[int(v) for v in sys.argv[3].split(',')]
show=[int(v) for v in sys.argv[4].split(',')] if len(sys.argv)>4 else []
cap=cv2.VideoCapture(f'data/QuantiPhy/simulation_{c}.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(cv2.GaussianBlur(im,(5,5),0).astype(np.float32)[y0:y1])
N=len(fr)
bg=np.median(np.stack(fr),axis=0)
if c in ('0157','0158'):
    bg[:,1450:]=np.median(np.stack(fr[38:])[:,:,1450:],axis=0)
if c=='0156':
    bg[:,1300:]=np.median(np.stack(fr[40:])[:,:,1300:],axis=0)
out=[]
for i in range(N):
    d=np.abs(fr[i]-bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: out.append(None); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    out.append((int(x),int(x+w-1),int(y+y0),int(y+h-1+y0),int(a)))
    if i in show:
        vis=cv2.cvtColor((np.clip(d*6,0,255)).astype(np.uint8),cv2.COLOR_GRAY2BGR)
        cnts,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(vis,cnts,-1,(0,0,255),1)
        xa=max(0,x-60); xb=min(1920,x+w+60)
        cv2.imwrite(f'research/next/audit3/sim2_13/img/tmask_{c}_{i}.png',vis[:,xa:xb])
for i,o in enumerate(out): print(i,o, (o[1]-o[0]+1) if o else None)
