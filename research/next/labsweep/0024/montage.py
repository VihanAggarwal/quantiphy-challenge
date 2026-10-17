import cv2, sys, numpy as np
v = sys.argv[1]; idxs=[int(x) for x in sys.argv[2].split(',')]
x0,y0,x1,y1 = [int(x) for x in sys.argv[3].split(',')]
scale=float(sys.argv[4]); ncol=int(sys.argv[5]); out=sys.argv[6]
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
fr={}; i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in idxs: fr[i]=f[y0:y1,x0:x1].copy()
    i+=1
tiles=[]
for i in idxs:
    g=cv2.resize(fr[i],None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC if scale>1 else cv2.INTER_AREA)
    cv2.putText(g,f'f{i}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    tiles.append(g)
while len(tiles)%ncol: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[k:k+ncol]) for k in range(0,len(tiles),ncol)]
cv2.imwrite(out,np.vstack(rows))
