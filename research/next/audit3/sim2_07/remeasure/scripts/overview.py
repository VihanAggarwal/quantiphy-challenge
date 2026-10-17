import cv2, numpy as np, sys
v=sys.argv[1]; out=sys.argv[2]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
print(len(fr))
idx=[0,12,18,24,30,36,42,48,54,59]
idx=[i for i in idx if i<len(fr)]
tiles=[]
for i in idx:
    t=cv2.resize(fr[i],(480,270)); cv2.putText(t,str(i),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2); tiles.append(t)
while len(tiles)%2: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[k:k+2]) for k in range(0,len(tiles),2)]
cv2.imwrite(out,np.vstack(rows))
