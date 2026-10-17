import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0054.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
sh=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/sh54.npy')*2  # full-res
# rider template: upper body box around shirt; initial centre half-res (1457,449)->full (2914,898)
cx,cy=2914,880
xs=[]
for k in range(len(fr)-1):
    T=fr[k][cy-110:cy+110,cx-60:cx+60]
    S=fr[k+1][cy-130:cy+130,cx-120:cx+80]
    r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mx,_,loc=cv2.minMaxLoc(r)
    # subpixel parabola in x
    lx,ly=loc
    if 0<lx<r.shape[1]-1:
        a,b,cc=r[ly,lx-1],r[ly,lx],r[ly,lx+1]; off=0.5*(a-cc)/(a-2*b+cc)
    else: off=0
    dx=(lx+off)-60; dy=ly-20
    xs.append((k,dx,dy,mx))
    cx+=int(round(dx)); cy+=dy
d=np.array([x[1] for x in xs]); 
bgd=np.diff(sh[:,0])
print('rider dx per frame (full res):'); print(np.round(d,1).tolist())
print('bg dx per frame:'); print(np.round(bgd,2).tolist())
rel=d-bgd[:len(d)]
print('mean rider dx %.2f, rel to bg %.2f px/frame, std %.2f'%(d.mean(),rel.mean(),rel.std()))
print('min score',min(x[3] for x in xs))
