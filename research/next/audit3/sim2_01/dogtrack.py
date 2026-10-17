import cv2, numpy as np, sys
# dogtrack.py clip x y (initial torso point at frame 0) half
c=sys.argv[1]; px,py=float(sys.argv[2]),float(sys.argv[3]); hs=int(sys.argv[4]); f0=int(sys.argv[5]) if len(sys.argv)>5 else 0
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
G=[]
while True:
    ok,f=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
pos={f0:(px,py)}
# forward and backward chained tracking with template from previous frame
def track(order):
    for a,b in zip(order[:-1],order[1:]):
        x,y=pos[a]; xi,yi=int(round(x)),int(round(y))
        T=G[a][yi-hs:yi+hs+1, xi-hs:xi+hs+1]
        R=40
        S=G[b][yi-hs-R:yi+hs+R+1, xi-hs-R:xi+hs+R+1]
        res=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
        _,mv,_,ml=cv2.minMaxLoc(res)
        # subpixel
        mx,my=ml
        dx=dy=0.0
        if 0<mx<res.shape[1]-1:
            l,cc,r=res[my,mx-1],res[my,mx],res[my,mx+1]; dx=0.5*(l-r)/(l-2*cc+r)
        if 0<my<res.shape[0]-1:
            u,cc,d=res[my-1,mx],res[my,mx],res[my+1,mx]; dy=0.5*(u-d)/(u-2*cc+d)
        nx=xi-R+mx+dx; ny=yi-R+my+dy
        # shift relative: template center moved from (xi,yi) to (xi + (mx-R)+dx, ...), plus subpixel of original
        pos[b]=(x+(mx-R)+dx, y+(my-R)+dy)
track(list(range(f0,len(G))))
if f0>0: track(list(range(f0,-1,-1)))
P=np.array([pos[i] for i in range(len(G))])
v=np.diff(P,axis=0); sp=np.hypot(v[:,0],v[:,1])
for i in range(1,len(G)): print(i,'%.1f %.1f  step %.2f'%(P[i,0],P[i,1],sp[i-1]))
def fitspeed(t,w):
    idx=np.arange(max(0,t-w),min(len(G),t+w+1))
    px_=np.polyfit(idx,P[idx,0],1)[0]; py_=np.polyfit(idx,P[idx,1],1)[0]
    return np.hypot(px_,py_)
for t in (24,36):
    print('t',t,'fit w2 %.2f w3 %.2f w5 %.2f  bwd1 %.2f  mean steps t-2..t+1 %.2f'%(fitspeed(t,2),fitspeed(t,3),fitspeed(t,5),sp[t-1],sp[t-3:t+1].mean()))
