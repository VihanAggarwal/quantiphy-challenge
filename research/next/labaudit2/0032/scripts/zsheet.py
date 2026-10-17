import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
r=sys.argv[1]; ks=[int(v) for v in sys.argv[2].split(',')]; y0,y1,x0,x1=[int(v) for v in sys.argv[3].split(',')]; sc=float(sys.argv[4]); tag=sys.argv[5]
fr=frames(r if r!='o' else '')
tiles=[]
for k in ks:
    c=cv2.resize(fr[k][y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
    cv2.putText(c,str(k),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2); tiles.append(c)
nc=int(sys.argv[6]) if len(sys.argv)>6 else 4
while len(tiles)%nc: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(D+'img/z_%s.png'%tag,np.vstack([np.hstack(tiles[i:i+nc]) for i in range(0,len(tiles),nc)]))
