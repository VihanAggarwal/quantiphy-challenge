import numpy as np, cv2
d=np.load('joint0302.npz'); T=d['T']; R=np.load('recon0302.npz'); a=R['a']; amax=a.max()
tips=np.load('tips0302.npy')
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0302.mp4')
for i in range(52): ok,fr=cap.read()
x0,y0,x1,y1=960,340,1260,600
crop=cv2.resize(fr[y0:y1,x0:x1],None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
for j in range(T.shape[1]):
    x,y=T[0,j]
    if x0<x<x1 and y0<y<y1:
        p=(int((x-x0)*3),int((y-y0)*3))
        cv2.circle(crop,p,5,(0,0,255),-1)
        cv2.putText(crop,f'{a[j]-amax:.2f}',(p[0]+6,p[1]-4),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
p=(int((tips[0,0]-x0)*3),int((tips[0,1]-y0)*3)); cv2.circle(crop,p,7,(0,255,0),2)
cv2.imwrite('frames/headzoom0302_051.png',crop)
