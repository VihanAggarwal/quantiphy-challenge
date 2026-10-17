import cv2, numpy as np, sys
v=sys.argv[1]
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
th=np.deg2rad(39.08)
u=np.array([np.cos(th), np.sin(th)])
n=np.array([-np.sin(th), np.cos(th)])
# axis line: from frame 18 centre (678.2,213.2) for seg
P0=np.array([678.2,213.2])
S=np.arange(-1300,700,0.5)
def strip(img):
    out=[]
    for t in np.arange(-2,2.1,1.0):
        xs=P0[0]+S*u[0]+t*n[0]; ys=P0[1]+S*u[1]+t*n[1]
        out.append(cv2.remap(img, xs.astype(np.float32).reshape(1,-1), ys.astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR, borderValue=-1).ravel())
    return np.array(out).mean(0)
ref=strip(fr[0])
prev=None
for i in range(len(fr)):
    s=strip(fr[i]); d=np.abs(s-ref); d[s<0]=0
    on=np.nonzero(d>40)[0]
    if len(on)==0: print(i,'none'); continue
    # largest run
    runs=np.split(on, np.nonzero(np.diff(on)>6)[0]+1)
    r=max(runs,key=len)
    nose=S[r[0]]; tail=S[r[-1]]
    print(i,'nose %.1f tail %.1f len %.1f'%(nose,tail,tail-nose))
