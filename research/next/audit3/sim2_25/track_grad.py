import cv2,numpy as np,sys
# track patch on gradient magnitude image, ref frame, chained matching against ref template only
v=sys.argv[1]; boxes=eval(sys.argv[2]); ref=int(sys.argv[3]); m=int(sys.argv[4]) if len(sys.argv)>4 else 60
mode=sys.argv[5] if len(sys.argv)>5 else 'grad'
c=cv2.VideoCapture(v); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    g=cv2.GaussianBlur(g,(0,0),1.5)
    if mode=='grad':
        gx=cv2.Sobel(g,cv2.CV_32F,1,0);gy=cv2.Sobel(g,cv2.CV_32F,0,1); g=np.sqrt(gx*gx+gy*gy)
    fr.append(g)
N=len(fr)
for (x,y,w,h) in boxes:
    T=fr[ref][y:y+h,x:x+w]; pos={}
    for direction in (1,-1):
        px,py=x,y; f=ref
        while 0<=f<N:
            x0=max(0,px-m);y0=max(0,py-m)
            S=fr[f][y0:py+h+m,x0:px+w+m]
            if S.shape[0]<h or S.shape[1]<w: break
            r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
            _,mv,_,ml=cv2.minMaxLoc(r); i,j=ml[1],ml[0]; dx=dy=0
            if 0<j<r.shape[1]-1:
                den=(r[i,j-1]-2*r[i,j]+r[i,j+1]); dx=(r[i,j-1]-r[i,j+1])/(2*den) if den!=0 else 0
            if 0<i<r.shape[0]-1:
                den=(r[i-1,j]-2*r[i,j]+r[i+1,j]); dy=(r[i-1,j]-r[i+1,j])/(2*den) if den!=0 else 0
            px,py=x0+j,y0+i; pos[f]=(x0+j+dx,y0+i+dy,mv); f+=direction
    ks=sorted(pos)
    print('box',(x,y,w,h),'frames',ks[0],ks[-1])
    print(' '.join('%d:%.1f,%.1f(%.2f)'%(f,*pos[f]) for f in ks if f%6==0 or f in(1,2,11,13,23,25,47,49)))
    xs=np.array([pos[f][0] for f in ks]); ys=np.array([pos[f][1] for f in ks])
    print('step dx',np.round(np.diff(xs),2).tolist())
    print('step dy',np.round(np.diff(ys),2).tolist())
