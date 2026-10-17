import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); acc=None; n=0
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    acc=g if acc is None else acc+g; n+=1
    if n>=10: break
g=acc/n
# row profile in a column range without markings
for x0 in [1100,1500]:
    col=g[880:1000,x0:x0+40].mean(1)
    pass
band=g[934:962,:].mean(0)
# high-pass
uniform_filter1d=lambda a,k: np.convolve(np.pad(a,k//2,mode="edge"),np.ones(k)/k,mode="valid")
hp=band-uniform_filter1d(band,41)
# find local minima below -8
mins=[x for x in range(3,1917) if hp[x]==hp[x-3:x+4].min() and hp[x]<-8]
# subpixel by parabola
sub=[]
for x in mins:
    l,m,r=hp[x-1],hp[x],hp[x+1]; d=0.5*(l-r)/(l-2*m+r); sub.append(x+d)
print('marks', ' '.join('%.1f(%.0f)'%(s,hp[int(round(s))]) for s in sub))
sub=np.array(sub); print('diffs',np.round(np.diff(sub),1))
