import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0062.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
g0=cv2.cvtColor(fr[90],cv2.COLOR_BGR2GRAY).astype(np.float32)
win=cv2.createHanningWindow((1920,1080),cv2.CV_32F)
for i in [0,60,66,72,78,84,100,120]:
    print('shift',i,np.round(cv2.phaseCorrelate(g0,cv2.cvtColor(fr[i],cv2.COLOR_BGR2GRAY).astype(np.float32),win)[0],2))
out=[]
for i in range(58,84):
    g=cv2.cvtColor(fr[i],cv2.COLOR_BGR2GRAY)
    m=(g<60).astype(np.uint8); m[:,1430:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
    pts=np.column_stack(np.where(lab==k))[:,::-1].astype(np.float32)
    rect=cv2.minAreaRect(pts)
    out.append((i,x,x+w,cen[k][0],cen[k][1],ar))
    print(i,'x %d-%d y %d-%d cx %.1f cy %.1f area %d rect %s'%(x,x+w,y,y+h,cen[k][0],cen[k][1],ar,str(np.round(rect[1],1))+' ang %.1f'%rect[2]))
o=np.array(out)
for lo,hi in [(67,79),(68,78),(70,79)]:
    for col,lab in [(2,'lead'),(3,'cx')]:
        sel=(o[:,0]>=lo)&(o[:,0]<=hi)
        t=o[sel,0]/30.; c=np.polyfit(t,o[sel,col],2); r=o[sel,col]-np.polyval(c,t)
        a=2*c[0]; t0=-c[1]/(2*c[0])
        print(lo,hi,lab,'a=%.0f'%a,'t_vertex=%.3f'%t0,'resid %.1f'%np.abs(r).max(),'v(2.5)px/s %.0f v(2.6) %.0f'%(2*c[0]*2.5+c[1],2*c[0]*2.6+c[1]),'disp2.2-2.5 %.1f'%(np.polyval(c,2.5)-np.polyval(c,2.2)))
