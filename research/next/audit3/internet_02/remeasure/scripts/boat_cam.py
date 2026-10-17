import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0070.mp4'
OUT='/home/user/quantiphy-challenge/research/next/audit3/internet_02/remeasure/'
c=cv2.VideoCapture(V); G=[]; frames={}
i=0
while True:
    ok,im=c.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    G.append(g[30:420,:])  # tree band only (boat is at y~430-560)
    i+=1
N=len(G); print('N',N)
win=cv2.createHanningWindow((G[0].shape[1],G[0].shape[0]),cv2.CV_32F)
cum=[(0.,0.)]
for k in range(1,N):
    (dx,dy),r=cv2.phaseCorrelate(G[k-1],G[k],win)
    cum.append((cum[-1][0]+dx,cum[-1][1]+dy))
cum=np.array(cum)
# also direct vs frame 30
d30=[]
for k in range(N):
    (dx,dy),r=cv2.phaseCorrelate(G[30],G[k],win); d30.append((dx,dy,r))
d30=np.array(d30)
np.savetxt(OUT+'boat_cam.txt',np.hstack([np.arange(N)[:,None],cum,d30]),fmt='%.3f',header='frame cumdx cumdy dx_vs30 dy_vs30 resp')
for k in range(0,N,10): print(k,'cum %.2f %.2f  vs30 %.2f %.2f r%.2f'%(cum[k,0],cum[k,1],*d30[k]))
