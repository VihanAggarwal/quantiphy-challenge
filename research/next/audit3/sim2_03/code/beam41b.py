import cv2, numpy as np, sys
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0041.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,36); ok,f=c.read()
f=f.astype(int)
step=np.array([12.4,-28.7])/31.3
x0=float(sys.argv[1]); y0=float(sys.argv[2]); n=int(sys.argv[3])
for i in range(0,n,2):
    p=np.array([x0,y0])+step*i
    xi,yi=int(round(p[0])),int(round(p[1]))
    B,G,R=f[yi,xi]
    print('%3d (%3d,%4d) R%3d G%3d B%3d'%(i,xi,yi,R,G,B))
