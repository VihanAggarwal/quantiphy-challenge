import cv2, numpy as np, sys
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
pre=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3]); out=sys.argv[4]
y0,y1,x0,x1=300,560,420,740
tiles=[]
for i in range(a,b):
    im=cv2.imread(R1+f'{pre}{i:02d}.png')[y0:y1,x0:x1].copy()
    cv2.putText(im,str(i),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    tiles.append(im)
while len(tiles)%4: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[k:k+4]) for k in range(0,len(tiles),4)]
cv2.imwrite(out,np.vstack(rows))
