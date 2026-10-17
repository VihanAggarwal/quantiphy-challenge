import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); G=[]
for k in range(50):
    ok,f=c.read()
    if not ok: break
    if k%4==0: G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
g=np.median(np.array(G),0)
sm=lambda a,k: np.convolve(np.pad(a,k//2,mode="edge"),np.ones(k)/k,mode="valid")
# per-row edges of pool
for (y0,y1) in [(470,600),(470,520),(560,600)]:
    band=g[y0:y1,:].mean(0); hp=band-sm(band,41)
    thr=-3*hp.std()
    mins=[x for x in range(8,1912) if hp[x]==hp[x-8:x+9].min() and hp[x]<thr]
    sub=[x+0.5*(hp[x-1]-hp[x+1])/(hp[x-1]-2*hp[x]+hp[x+1]) for x in mins]
    print('band',y0,y1,'thr %.1f'%thr,' '.join('%.1f(%.0f)'%(s,hp[int(round(s))]) for s in sub)); print('  diffs',np.round(np.diff(sub),1))
# transverse joint rows near the pool edge
colp=g[400:640,1450:1900].mean(1); hp=colp-sm(colp,21)
print('row minima', [(400+i, round(float(hp[i]),1)) for i in range(5,235) if hp[i]==hp[i-5:i+6].min() and hp[i]<-5])
