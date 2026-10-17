import cv2, numpy as np, sys
p=sys.argv[1]; reff=int(sys.argv[2]); f0,f1=[int(v) for v in sys.argv[3].split(',')]
strips=[[int(v) for v in s.split(':')] for s in sys.argv[4].split(',')]  # x0:x1:fstart:fend
bands=[(y,y+80) for y in range(int(sys.argv[5]),1080-79,40)]
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
def prof(g,x0,x1):
    pr=g[:,x0:x1].mean(1); return pr-cv2.GaussianBlur(pr.reshape(-1,1),(0,0),10).ravel()
def shift1d(a,b,maxs=15):
    # find s such that b(y)=a(y-s); subpixel via parabola on SSD
    best=[]
    n=len(a)
    for s in range(-maxs,maxs+1):
        lo=max(0,s); hi=min(n,n+s)
        e=((b[lo:hi]-a[lo-s:hi-s])**2).mean()
        best.append(e)
    best=np.array(best); i=int(np.argmin(best))
    if 0<i<len(best)-1:
        A,B,C=best[i-1],best[i],best[i+1]; d=A-2*B+C; ds=0.5*(A-C)/d if d else 0
    else: ds=0
    return i-maxs+ds
res=[]
for f in range(f0,f1+1):
    for x0,x1,fs,fe in strips:
        if not (fs<=f<=fe): continue
        Pr=prof(G[reff],x0,x1); Pf=prof(G[f],x0,x1)
        ys=[];ds=[]
        for y0,y1 in bands:
            m=25
            s=shift1d(Pr[y0-m:y1+m],Pf[y0-m:y1+m])
            ys.append((y0+y1)/2); ds.append(s)
        ys=np.array(ys); ds=np.array(ds)
        c=np.polyfit(ys-540,ds,1)
        r=ds-np.polyval(c,ys-540)
        res.append((f,x0,c[0],c[1],r.std()))
        print('%d strip %d-%d  k=%.5f dy0=%.2f rms=%.2f  dys=%s'%(f,x0,x1,c[0],c[1],r.std(),np.round(ds,1)))
np.savetxt(sys.argv[6],np.array(res),fmt='%.5f')
