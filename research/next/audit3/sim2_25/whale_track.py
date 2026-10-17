import cv2,numpy as np,sys
v=sys.argv[1]; boxes=eval(sys.argv[2])  # list of (x,y,w,h) in full res at ref frame
ref=int(sys.argv[3])
c=cv2.VideoCapture(v); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
print('n',len(fr))
for (x,y,w,h) in boxes:
    T=fr[ref][y:y+h,x:x+w]
    pos={}
    # track sequentially from ref outward
    for direction in (1,-1):
        px,py=x,y
        f=ref
        while 0<=f<len(fr):
            m=80
            x0=max(0,px-m);y0=max(0,py-m)
            S=fr[f][y0:py+h+m,x0:px+w+m]
            if S.shape[0]<h or S.shape[1]<w: break
            r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
            _,mv,_,ml=cv2.minMaxLoc(r)
            # subpixel
            i,j=ml[1],ml[0]
            dx=dy=0
            if 0<j<r.shape[1]-1: dx=(r[i,j-1]-r[i,j+1])/(2*(r[i,j-1]-2*r[i,j]+r[i,j+1]))
            if 0<i<r.shape[0]-1: dy=(r[i-1,j]-r[i+1,j])/(2*(r[i-1,j]-2*r[i,j]+r[i+1,j]))
            px,py=x0+j,y0+i
            pos[f]=(x0+j+dx,y0+i+dy,mv)
            f+=direction
    ks=sorted(pos)
    print('box',x,y,w,h)
    for f in ks:
        if f%4==0 or f in (11,12,13,23,24,25):
            print(f,'%.2f %.2f %.3f'%pos[f])
    xs=np.array([pos[f][0] for f in ks]); 
    d=np.diff(xs); print('mean dx/frame',d.mean(), 'by 12-frame windows',[round(float((pos[f+12][0]-pos[f][0])/12),2) for f in range(ks[0],ks[-1]-12,12)])
