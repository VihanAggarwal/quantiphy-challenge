import cv2, numpy as np, sys
def frames(vid):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4'); out=[]
    while True:
        ok,fr=cap.read()
        if not ok: break
        out.append(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY).astype(np.float32))
    return np.array(out)
vid=sys.argv[1]; nfit=int(sys.argv[2]); F=frames(vid)
bg=np.median(F,axis=0)
rec=[]
for k in range(0,16):
    d=np.abs(F[k]-bg); m=(d>20).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(k,'none'); continue
    i=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); x,y,w,h,a=st[i]
    # weighted centroid using difference magnitude
    ys,xs=np.where(lab==i); wts=d[ys,xs]
    rec.append((k,cen[i][0],cen[i][1],y,y+h-1,x,x+w-1,a))
    print('k=%2d cx=%.2f cy=%.2f top=%d bot=%d left=%d right=%d w=%d area=%d'%(k,cen[i][0],cen[i][1],y,y+h-1,x,x+w-1,w,a))
rec=np.array(rec)
k=rec[:nfit,0]
for col,name in [(2,'cy'),(3,'top'),(4,'bot')]:
    p=np.polyfit(k,rec[:nfit,col],2); r=rec[:nfit,col]-np.polyval(p,k)
    print(name,'a_px/frame^2=%.3f  t0(frames)=%.3f rms=%.2f'%(2*p[0], -p[1]/(2*p[0]), r.std()))
