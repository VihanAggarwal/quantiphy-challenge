import cv2, numpy as np, sys
v=sys.argv[1]; i=int(sys.argv[2]); y0,y1,x0,x1=map(int,sys.argv[3].split(','))
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4'); c.set(1,i); im=c.read()[1]
crop=im[y0:y1,x0:x1]
z=float(sys.argv[4]) if len(sys.argv)>4 else 2
big=cv2.resize(crop,None,fx=z,fy=z,interpolation=cv2.INTER_NEAREST)
# grid lines every 10 px (original)
for gx in range(0,x1-x0,10):
    col=(0,255,255) if (x0+gx)%50==0 else (90,90,90)
    if (x0+gx)%50==0: big[:, int(gx*z)]=col
for gy in range(0,y1-y0,10):
    if (y0+gy)%50==0: big[int(gy*z),:]=(0,255,255)
out=f'prof_{v}_{i}_{x0}_{y0}.png'; cv2.imwrite(out,big); print(out,big.shape)
