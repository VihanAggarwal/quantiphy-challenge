import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0061.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
out=[]
for i in list(range(30,62)):
    g=cv2.cvtColor(fr[i],cv2.COLOR_BGR2GRAY).astype(np.float32)
    mu=cv2.blur(g,(21,21)); sd=np.sqrt(np.maximum(cv2.blur(g*g,(21,21))-mu*mu,0))
    m=((mu>150)&(sd<14)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
    # extend by 10px (box filter erosion of edges ~ half window)
    out.append((i,x,x+w,y,y+h,cen[k][0],cen[k][1],ar))
    print(i,'x %d-%d y %d-%d w %d h %d cx %.1f cy %.1f area %d'%(x,x+w,y,y+h,w,h,cen[k][0],cen[k][1],ar))
o=np.array(out)
np.savetxt('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/t61c.txt',o,fmt='%.1f')
def fit(sel,col,lab):
    t=o[sel,0]/30.0; x=o[sel,col]
    c=np.polyfit(t,x,2); r=x-np.polyval(c,t)
    print(lab,'frames',o[sel,0].astype(int).tolist(),'a=%.0f px/s2'%(2*c[0]),'resid max %.1f'%np.abs(r).max(), 'coef',np.round(c,1))
    return c
for col,lab in [(1,'left'),(2,'right'),(5,'cx')]:
    fit((o[:,0]>=40)&(o[:,0]<=44),col,'fall '+lab)
    fit((o[:,0]>=41)&(o[:,0]<=44),col,'fall41 '+lab)
    fit((o[:,0]>=48)&(o[:,0]<=56),col,'rebound '+lab)
    fit((o[:,0]>=47)&(o[:,0]<=57),col,'rebound47-57 '+lab)
