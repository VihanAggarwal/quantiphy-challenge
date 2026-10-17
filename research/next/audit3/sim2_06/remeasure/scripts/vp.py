import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); G=[]
for k in range(50):
    ok,f=c.read()
    if not ok: break
    if k%5==0: G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
g=np.median(np.array(G,np.float32),0)
sm=lambda a,k: np.convolve(np.pad(a,k//2,mode="edge"),np.ones(k)/k,mode="valid")
pts={}
for y in range(800,924,2):
    row=g[y-1:y+2,:].mean(0); hp=row-sm(row,31)
    mins=[x for x in range(4,1916) if hp[x]==hp[x-4:x+5].min() and hp[x]<-6]
    out=[]
    for x in mins:
        l,m,r=hp[x-1],hp[x],hp[x+1]; out.append(x+0.5*(l-r)/(l-2*m+r))
    pts[y]=out
# link: start from row 922 minima, follow upward
lines=[]
for x0 in pts[922]:
    tr=[(922,x0)]; x=x0; prev=None
    for y in range(920,798,-2):
        cand=[c_ for c_ in pts[y] if abs(c_-x)<3.5]
        if not cand: break
        xn=min(cand,key=lambda c_:abs(c_-x)); tr.append((y,xn)); x=xn
    if len(tr)>=12:
        T=np.array(tr); p=np.polyfit(T[:,0],T[:,1],1); res=T[:,1]-np.polyval(p,T[:,0])
        lines.append((p[0],p[1],len(tr),res.std(),x0))
for L in lines: print('slope dx/dy %.4f x@922 %.1f n %d rms %.2f'%(L[0],np.polyval(L[:2],922),L[2],L[3]))
# intersect pairs of lines with |slope|>0.05
L=[l for l in lines if abs(l[0])>0.05 and l[3]<1.0]
ys=[]
for i in range(len(L)):
    for j in range(i+1,len(L)):
        a1,b1=L[i][:2]; a2,b2=L[j][:2]
        if abs(a1-a2)<0.1: continue
        y=(b2-b1)/(a1-a2); ys.append((y,a1*y+b1))
ys=np.array(ys); print('n pairs',len(ys),'VP y median %.1f x median %.1f'%(np.median(ys[:,0]),np.median(ys[:,1])))
# least squares VP: x = a*y + b for each line, minimize over (xv,yv): xv - a*yv - b = 0
A=np.array([[1,-l[0]] for l in L]); B=np.array([l[1] for l in L])
sol=np.linalg.lstsq(A,B,rcond=None)[0]; print('LSQ VP x %.1f y %.1f'%(sol[0],sol[1]))
