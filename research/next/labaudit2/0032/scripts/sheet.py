import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
r=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3])
fr=frames(r)
tiles=[]
for k in range(a,b):
    c=fr[k][340:540,420:1000].copy()
    cv2.putText(c,str(k),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    tiles.append(c)
while len(tiles)%4: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+4]) for i in range(0,len(tiles),4)]
cv2.imwrite(D+'img/sheet_%s_%d_%d.png'%(r,a,b),np.vstack(rows))
