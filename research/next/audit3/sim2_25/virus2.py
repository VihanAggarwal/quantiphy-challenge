import cv2,numpy as np,sys
v=sys.argv[1]; f0=2666.7; cx0,cy0=960,540
c=cv2.VideoCapture(v); f=0; rows=[]
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(71,71))
while True:
    ok,im=c.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    m=(g<150).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,k)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    for i in range(1,n):
        if st[i,4]<20000: continue
        x,y,w,h=st[i,:4]
        if x<=0 or y<=0 or x+w>=g.shape[1] or y+h>=g.shape[0]: continue
        cnts,_=cv2.findContours((lab==i).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        (ex,ey),(a1,a2),ang=cv2.fitEllipse(cnts[0])
        out.append((ex,ey,min(a1,a2)/2,max(a1,a2)/2))
    out.sort(); rows.append(out); f+=1
for f,o in enumerate(rows):
    if f in (1,2,6,12,18,23,24,30,35,36,40,46,47,48):
        s=[]
        for (ex,ey,b,a) in o:
            d=np.hypot(ex-cx0,ey-cy0); pred=1/np.cos(np.arctan(d/f0))
            s.append('(%.1f,%.1f) b%.2f a%.2f a/b%.4f pred%.4f'%(ex,ey,b,a,a/b,pred))
        print(f,' | '.join(s))
import pickle; pickle.dump(rows,open(sys.argv[2],'wb'))
