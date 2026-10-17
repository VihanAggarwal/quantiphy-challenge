import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0047.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
ref=g[29]; win=cv2.createHanningWindow((1920,380),cv2.CV_32F)
sh=np.array([cv2.phaseCorrelate(ref[700:1080],g[i][700:1080],win)[0] for i in range(len(g))])
al=[cv2.warpAffine(f,np.float32([[1,0,-sh[i,0]],[0,1,-sh[i,1]]]),(1920,1080),borderMode=cv2.BORDER_REPLICATE) for i,f in enumerate(fr)]
# template from frame 10 around centroid (861,550)
T=al[10][550-130:550+130,861-150:861+150]
pos={}
for i in range(1,21):
    r=cv2.matchTemplate(al[i],T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    # subpixel via parabola
    x,y=loc
    if 0<x<r.shape[1]-1:
        a,b,c=r[y,x-1],r[y,x],r[y,x+1]; dx=0.5*(a-c)/(a-2*b+c)
    else: dx=0
    if 0<y<r.shape[0]-1:
        a,b,c=r[y-1,x],r[y,x],r[y+1,x]; dy=0.5*(a-c)/(a-2*b+c)
    else: dy=0
    pos[i]=(x+dx+150-861+861, y+dy+130)  # template centre
    print(i,'score %.3f'%mx,'centre x %.1f y %.1f'%(x+dx+150,y+dy+130))
xs=np.array([pos[i][0] for i in range(1,21)]); ys=np.array([pos[i][1] for i in range(1,21)])
d=np.hypot(np.diff(xs),np.diff(ys)); print('step px',np.round(d,1).tolist())
f=np.arange(1,21)
for lo,hi in [(3,9),(12,18),(4,19)]:
    s=(f>=lo)&(f<=hi); c=np.polyfit(f[s],xs[s],1); cy=np.polyfit(f[s],ys[s],1)
    print(lo,hi,'vx %.2f vy %.2f |v| %.2f px/frame'%(c[0],cy[0],np.hypot(c[0],cy[0])))
print('disp f3->f9 %.1f px'%np.hypot(xs[8]-xs[2],ys[8]-ys[2]))
