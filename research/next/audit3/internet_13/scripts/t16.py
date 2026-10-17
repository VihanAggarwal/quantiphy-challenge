import cv2,numpy as np
v=cv2.VideoCapture('data/QuantiPhy/internet_0016.mp4')
fr=[]
for f in range(20):
    ok,im=v.read(); fr.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY))
# template from frame 15 ball (1140,3433), r~20
t=fr[15][3433-22:3433+23,1140-22:1140+23]
pos=[]
for f in range(20):
    roi=fr[f][3300:3600,1000:1250]
    r=cv2.matchTemplate(roi,t,cv2.TM_CCOEFF_NORMED)
    _,mx,_,ml=cv2.minMaxLoc(r)
    # subpixel
    x,y=ml
    if 0<x<r.shape[1]-1 and 0<y<r.shape[0]-1:
        dx=(r[y,x+1]-r[y,x-1])/(2*(2*r[y,x]-r[y,x+1]-r[y,x-1])); dy=(r[y+1,x]-r[y-1,x])/(2*(2*r[y,x]-r[y+1,x]-r[y-1,x]))
    else: dx=dy=0
    p=(1000+x+dx+22,3300+y+dy+22); pos.append(p)
    print(f,'%.1f %.1f ncc %.2f'%(p[0],p[1],mx))
pos=np.array(pos)
st=np.linalg.norm(np.diff(pos,axis=0),axis=1); print('steps',np.round(st,1))
for n in (5,7,9):
    t_=np.arange(n); px=np.polyfit(t_,pos[:n,0],2); py=np.polyfit(t_,pos[:n,1],2)
    print(n,'v0 px/frame', np.hypot(px[1],py[1]))
