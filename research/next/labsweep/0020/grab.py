import cv2, sys, numpy as np
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
scale=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
c=cv2.VideoCapture(vid); imgs={}
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames: imgs[i]=f
    i+=1
tiles=[]
for k in frames:
    f=imgs[k].copy(); cv2.putText(f,str(k),(20,60),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),4)
    tiles.append(cv2.resize(f,None,fx=scale,fy=scale))
rows=[]
n=2
for j in range(0,len(tiles),n):
    r=tiles[j:j+n]
    while len(r)<n: r.append(np.zeros_like(tiles[0]))
    rows.append(np.hstack(r))
cv2.imwrite(out,np.vstack(rows))
