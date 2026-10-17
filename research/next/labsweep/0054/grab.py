import cv2, sys, numpy as np
# usage: grab.py video frames(comma) out_prefix [scale] [x0 y0 x1 y1]
v=sys.argv[1]; fr=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
sc=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
box=[int(x) for x in sys.argv[5:9]] if len(sys.argv)>8 else None
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0054{v}.mp4')
frames=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in fr: frames.append((i,f))
    i+=1
imgs=[]
for i,f in frames:
    if box: f=f[box[1]:box[3],box[0]:box[2]]
    f=cv2.resize(f,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
    cv2.putText(f,str(i),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    imgs.append(f)
# tile 2 columns
cols=2 if len(imgs)>1 else 1
rows=[]
for k in range(0,len(imgs),cols):
    r=imgs[k:k+cols]
    while len(r)<cols: r.append(np.zeros_like(imgs[0]))
    rows.append(np.hstack(r))
cv2.imwrite(out,np.vstack(rows))
