import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0047/scripts')
from track import *
rend=sys.argv[1] if len(sys.argv)>1 else 'x'
out={}
prev=None
for n in range(0,49):
    f=cv2.imread(D+f'frames/{rend}_{n:02d}.png').astype(int)
    if rend=='x':
        green=(f[:,:,1]>150)&(f[:,:,0]<110)&(f[:,:,2]<110)
    else:
        raise SystemExit
    fg=~green
    fg[700:]=False  # watermark/bottom band handled separately
    fg8=fg.astype(np.uint8)
    # boundary pixels of fg adjacent to green
    er=cv2.erode(fg8,np.ones((3,3),np.uint8))
    bd=(fg8==1)&(er==0)
    ys,xs=np.nonzero(bd)
    pts=np.stack([xs,ys],1).astype(float)
    out[n]=pts.tolist()
json.dump(out,open(D+f'bd_{rend}.json','w'))
