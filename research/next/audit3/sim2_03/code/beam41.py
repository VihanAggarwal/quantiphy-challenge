import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0041.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,36); ok,f=c.read()
f=f.astype(float)
step=np.array([12.4,-28.7])/31.3  # unit px step along beam (far direction), 31.3 px per m
def cls(p):
    B,G,R=p
    if R>150 and G<90: return 'r'   # red hull
    if R>170 and G>170 and B>170: return 'W'
    if R>120 and G>120 and B>120: return 'w'
    if G>R+5: return 'g'  # water
    return '.'
import sys
for x0 in [int(a) for a in sys.argv[1:]]:
    # start below hull: find y where near water at column x0
    start=np.array([x0, 1040.])
    s=''
    pts=[]
    for i in range(0,170):
        p=start+step*i
        xi,yi=int(round(p[0])),int(round(p[1]))
        if yi<0: break
        s+=cls(f[yi,xi]); pts.append((xi,yi))
    print(x0, s)
