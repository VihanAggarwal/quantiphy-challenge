import cv2,sys,numpy as np
v=sys.argv[1]; x0,y0,x1,y1=[int(t) for t in sys.argv[2].split(',')]; fr=[int(t) for t in sys.argv[3].split(',')]; sc=float(sys.argv[4]); ncol=int(sys.argv[5]); out=sys.argv[6]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
tiles=[];i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in fr:
        g=f[y0:y1,x0:x1].copy(); g=cv2.resize(g,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
        cv2.putText(g,str(i),(3,18),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        tiles.append(g)
    i+=1
h,w=tiles[0].shape[:2]
while len(tiles)%ncol: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[r*ncol:(r+1)*ncol]) for r in range(len(tiles)//ncol)]
cv2.imwrite(out,np.vstack(rows))
