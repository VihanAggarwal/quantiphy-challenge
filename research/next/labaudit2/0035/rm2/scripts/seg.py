# Segment soccer ball (white/black) and basketball (orange) in the green-screen render ax.
import cv2, numpy as np, json, sys
V='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0035ax.mp4'
c=cv2.VideoCapture(V); frames=[]
while True:
    ok,f=c.read()
    if not ok: break
    frames.append(f)
out=[]
for i,f in enumerate(frames):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    b,g,r=[f[...,k].astype(int) for k in range(3)]
    green=(g>150)&(r<120)&(b<120)
    fg=(~green).astype(np.uint8)
    # orange basketball
    orange=((hsv[...,0]>=3)&(hsv[...,0]<=20)&(hsv[...,1]>120)&(hsv[...,2]>80)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg)
    comps=[]
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<200: continue
        comps.append(dict(k=int(k),x=int(x),y=int(y),w=int(w),h=int(h),a=int(a),cx=float(cen[k][0]),cy=float(cen[k][1]),
                          orange=float(orange[lab==k].mean())))
    out.append(comps)
for i,cs in enumerate(out):
    print(i,[ (c['x'],c['y'],c['w'],c['h'],c['a'],round(c['orange'],2)) for c in cs if c['a']<20000])
