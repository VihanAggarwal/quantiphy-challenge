import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from frames import load
from tplane import *
BC=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/book_corners.json'))
f=711.; n,cP,_,_,_=pose(f)
r=sys.argv[1] if len(sys.argv)>1 else ''
fr=load(r)
im=np.median(np.stack([f_.astype(np.float32) for f_ in fr[30:49]]),0)
TR,BR,BL,TL=[np.array(p) for p in BC[r or 'o']]
ldir=((BL-TL)+(BR-TR)); ldir/=np.linalg.norm(ldir)
verbose=len(sys.argv)>2
res=[]
for fw in [0.3,0.5,0.7]:
    a=TL+(TR-TL)*fw; b=BL+(BR-BL)*fw; mid=(a+b)/2
    ts=np.arange(-40,41,1.0)
    vals=[cv2.getRectSubPix(im,(1,1),(float(p[0]),float(p[1])))[0,0] for p in mid[None,:]+ts[:,None]*ldir[None,:]]
    vals=np.array(vals)
    if verbose:
        print('fw',fw,'mid',np.round(mid,1),'ldir',np.round(ldir,3))
        for t,v in zip(ts,vals): print(f'  t={t:+4.0f} xy=({mid[0]+t*ldir[0]:.1f},{mid[1]+t*ldir[1]:.1f}) BGR={np.round(v).astype(int)} B-R={v[0]-v[2]:+.0f} V={v.mean():.0f}')
