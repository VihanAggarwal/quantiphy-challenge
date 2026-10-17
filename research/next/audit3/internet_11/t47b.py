import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0047.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im.astype(np.float32))
g=[cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
ref=g[29]; win=cv2.createHanningWindow((1920,380),cv2.CV_32F)
sh=np.array([cv2.phaseCorrelate(ref[700:1080],g[i][700:1080],win)[0] for i in range(len(g))])
al=[]
for i,f in enumerate(fr):
    M=np.float32([[1,0,-sh[i,0]],[0,1,-sh[i,1]]])
    al.append(cv2.warpAffine(f,M,(1920,1080),borderMode=cv2.BORDER_REPLICATE))
bg=np.median(np.stack(al[::1]),axis=0)  # ball moves fast so median is bg
out=[]
for i,a in enumerate(al):
    d=np.abs(a-bg).max(axis=2)
    d[:30]=0;d[-30:]=0
    m=(d>35).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
        if ar<2000: continue
        out.append((i,cen[k][0],cen[k][1],x,y,w,h,ar))
        print(i,'cx %.1f cy %.1f x %d-%d y %d-%d w %d h %d area %d eqd %.0f'%(cen[k][0],cen[k][1],x,x+w,y,y+h,w,h,ar,2*np.sqrt(ar/np.pi)))
        if i in (8,15):
            crop=a[max(0,y-40):y+h+40,max(0,x-40):x+w+40].astype(np.uint8).copy()
            cv2.imwrite('research/next/audit3/internet_11/png/b47_%d.png'%i,crop)
o=np.array(out); 
import numpy.polynomial.polynomial as P
sel=(o[:,0]>=3)&(o[:,0]<=19)
c=np.polyfit(o[sel,0],o[sel,1],2); print('cx quad fit',c,'v at 15 px/frame',2*c[0]*15+c[1])
c1=np.polyfit(o[sel,0],o[sel,1],1); print('lin',c1)
print('frame diffs',np.round(np.diff(o[:,1]),1).tolist())
