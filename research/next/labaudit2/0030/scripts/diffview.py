import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0030/scripts')
from track import frames
S=frames('s'); O=frames(''); X=frames('x')
ks=[int(k) for k in sys.argv[1].split(',')]
import json
H=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0030/track_hull.json'))['s']
tiles=[]
for k in ks:
    cx,cy=int(H[k]['hx']),int(H[k]['hy']); h=45
    sl=(slice(cy-h,cy+h),slice(cx-h,cx+h))
    s=S[k][sl].astype(int); o=O[k][sl].astype(int); x=X[k][sl].astype(int)
    dso=np.abs(s-o).sum(2); dsx=np.abs(s-x).sum(2)
    a=np.clip(dso,0,255).astype(np.uint8); b=np.clip(dsx,0,255).astype(np.uint8)
    row=np.hstack([S[k][sl],O[k][sl],X[k][sl],cv2.cvtColor(a,cv2.COLOR_GRAY2BGR),cv2.cvtColor(b,cv2.COLOR_GRAY2BGR)])
    row=cv2.resize(row,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
    cv2.putText(row,f'v{k}',(5,22),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2)
    tiles.append(row)
cv2.imwrite(sys.argv[2],np.vstack(tiles))
