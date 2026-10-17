import cv2,numpy as np,sys
v=sys.argv[1]
c=cv2.VideoCapture(v); rows=[]; f=0
while True:
    ok,im=c.read()
    if not ok: break
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    b,g,r=[im[:,:,i].astype(float) for i in range(3)]
    yel=(r+g)/2-b
    m=(yel>60)&(hsv[:,:,1]>90)
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        i=1+np.argmax(st[1:,4]); x,y,w,h,a=st[i]
        ys,xs=np.nonzero(lab==i); wts=np.clip(yel[ys,xs],0,None)
        rows.append((f,x,y,w,h,a,(xs*wts).sum()/wts.sum(),(ys*wts).sum()/wts.sum()))
    f+=1
R=np.array(rows)
for r in R[::4]: print('%d x%d y%d w%d h%d a%d c(%.1f,%.1f)'%tuple(r))
sel=(R[:,2]>2)&(R[:,2]+R[:,4]<1918)
t=R[sel,0]/24.; y=R[sel,7]
for lo,hi in [(0,80),(0,40),(20,76),(1,60)]:
    s=(R[sel,0]>=lo)&(R[sel,0]<=hi)
    p=np.polyfit(t[s],y[s],2); print('fit',lo,hi,'a=%.2f px/s2 v0=%.2f vertex t=%.3f'%(2*p[0],p[1],-p[1]/(2*p[0])), 'rms %.2f'%np.std(y[s]-np.polyval(p,t[s])))
