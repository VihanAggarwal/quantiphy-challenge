import sys
from common import *
take=sys.argv[1]; key=sys.argv[2]; ks=[int(x) for x in sys.argv[3].split(',')]; outname=sys.argv[4]
half=int(sys.argv[5]) if len(sys.argv)>5 else 50; sc=int(sys.argv[6]) if len(sys.argv)>6 else 3
tr=json.load(open(f'{OUT}/tr_{take[0]}.json'))
fr=frames(take)
tiles=[]
for k in ks:
    d=tr[key].get(str(k))
    cx,cy=(int(round(d['cx'])),int(round(d['cy']))) if d else (640,360)
    c=fr[k][max(cy-half,0):cy+half,max(cx-half,0):cx+half].copy()
    c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    if d:
        ox,oy=max(cx-half,0),max(cy-half,0)
        cv2.circle(c,(int((d['cx']-ox)*sc),int((d['cy']-oy)*sc)),3,(0,0,255),-1)
        cv2.circle(c,(int((d['cx']-ox)*sc),int((d['cy']-oy)*sc)),int(d['minor']/2*sc),(0,0,255),1)
    cv2.putText(c,str(k),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    tiles.append(c)
cv2.imwrite(f'{OUT}/frames/{outname}',np.hstack(tiles))
