import cv2,numpy as np,sys,pickle
v=sys.argv[1]; which=int(sys.argv[2]); frames=list(map(int,sys.argv[3].split(',')))
rows=pickle.load(open(sys.argv[4],'rb'))
c=cv2.VideoCapture(v); F={}
i=0
while True:
    ok,im=c.read()
    if not ok: break
    if i in frames or i==1: F[i]=cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32),(0,0),1.0)
    i+=1
ex,ey=rows[1][which][:2]; R=280
T0=F[1][int(ey-R):int(ey+R),int(ex-R):int(ex+R)]
for f in frames:
    o=rows[f][which] if len(rows[f])>which else None
    if o is None: continue
    px,py=o[:2]; best=[]
    for s in np.arange(0.96,1.12,0.005):
        T=cv2.resize(T0,None,fx=s,fy=s,interpolation=cv2.INTER_LINEAR)
        h,w=T.shape; m=20
        y0=int(py-h/2-m); x0=int(px-w/2-m)
        if y0<0 or x0<0 or y0+h+2*m>F[f].shape[0] or x0+w+2*m>F[f].shape[1]: best=None;break
        S=F[f][y0:y0+h+2*m,x0:x0+w+2*m]
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
        best.append((s,mv,x0+ml[0]+w/2,y0+ml[1]+h/2))
    if not best: print(f,'edge'); continue
    b=np.array(best); j=b[:,1].argmax()
    if 0<j<len(b)-1:
        y1,y2,y3=b[j-1,1],b[j,1],b[j+1,1]; sref=b[j,0]+0.005*(y1-y3)/(2*(y1-2*y2+y3))
    else: sref=b[j,0]
    print(f,'scale %.4f score %.3f centre (%.1f,%.1f)'%(sref,b[j,1],b[j,2],b[j,3]))
