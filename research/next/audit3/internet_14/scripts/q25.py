import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0025.mp4')
frames={}
want=[0,150,300,472]
f=0
while True:
    ok,im=c.read()
    if not ok: break
    if f in want: frames[f]=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    f+=1
print('nframes',f)
g0=frames[0]
# boat template: rows 630-690, x 690-1060
T=g0[630:690,690:1060]
bg=g0[300:500,200:1700]  # mountains
for k in want[1:]:
    g=frames[k]
    r=cv2.matchTemplate(g[600:720,:],T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
    # background shift via phase correlation on mountain band
    a=np.float32(g0[100:450,300:1600]); b=np.float32(g[100:450,300:1600])
    sh,_=cv2.phaseCorrelate(a,b)
    print(k, 'boat x',ml[0]-690, 'score',round(mv,3),'bg shift',sh)
