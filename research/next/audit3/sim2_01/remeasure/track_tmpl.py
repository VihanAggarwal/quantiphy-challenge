import cv2, numpy as np, sys
# frame-to-frame template tracking of a cat part
v=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6]); ylo,yhi=int(sys.argv[6]),int(sys.argv[7])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
tw,th=x1-x0,y1-y0
ix,iy=x0,y0; X=[float(x0)]; Y=[y0]; SC=[1.0]
for i in range(1,len(fr)):
    T=fr[i-1][iy:iy+th,ix:ix+tw]
    sx0=max(0,ix-60); sx1=min(1920,ix+tw+80)
    S=fr[i][ylo:yhi,sx0:sx1]
    R=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
    _,mv,_,(xx,yy)=cv2.minMaxLoc(R)
    dx=0.0
    if 0<xx<R.shape[1]-1:
        a,b,cc=R[yy,xx-1],R[yy,xx],R[yy,xx+1]
        den=(a-2*b+cc)
        if den!=0: dx=0.5*(a-cc)/den
    # accumulate subpixel displacement relative to previous integer position
    newx=sx0+xx+dx
    X.append(X[-1]+(newx-ix)); Y.append(ylo+yy); SC.append(mv)
    ix=sx0+xx; iy=ylo+yy
X=np.array(X); t=np.arange(len(X))
print('per-frame dx:',' '.join(f'{v:.1f}' for v in np.diff(X)))
p=np.polyfit(t,X,1); print('fit slope %.3f px/frame, rms %.2f; mean dx %.3f; median dx %.3f'%(p[0],(X-np.polyval(p,t)).std(),np.diff(X).mean(),np.median(np.diff(X))))
print('y range',min(Y),max(Y),' min score %.2f'%min(SC))
