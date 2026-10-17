import cv2, numpy as np, sys
sys.path.insert(0,'scripts')
from frames import load
r=sys.argv[1]; k0=int(sys.argv[2]); k1=int(sys.argv[3])
x0,y0,x1,y1=[int(v) for v in sys.argv[4].split(',')]
sc=int(sys.argv[5]) if len(sys.argv)>5 else 3
fr=load(r)
tiles=[]
for k in range(k0,k1):
    c=fr[k][y0:y1,x0:x1].copy()
    c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    cv2.putText(c,str(k),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    tiles.append(c)
nc=6
while len(tiles)%nc: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+nc]) for i in range(0,len(tiles),nc)]
cv2.imwrite(sys.argv[6] if len(sys.argv)>6 else f'img/mont_{r or "o"}_{k0}_{k1}.png',np.vstack(rows))
