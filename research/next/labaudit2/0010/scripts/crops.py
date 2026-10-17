import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/track.json'))
sel=[int(a) for a in sys.argv[1].split(',')]
tiles=[]
for r in ['s','','X']:
    fr=frames(r); row=[]
    for i in sel:
        u,v=T['s'][i]['u'],T['s'][i]['v']
        x0,y0=int(u)-30,int(v)-30
        c=fr[i][y0:y0+60,x0:x0+60].copy()
        c=cv2.resize(c,(240,240),interpolation=cv2.INTER_NEAREST)
        cv2.putText(c,f'{r or "o"}{i}',(5,20),0,0.6,(255,0,255),2)
        row.append(c)
    tiles.append(np.hstack(row))
cv2.imwrite(sys.argv[2],np.vstack(tiles))
