import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from frames import load
BC=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/book_corners.json'))
fr=load('')
im=np.median(np.stack([f_.astype(np.float32) for f_ in fr[30:49]]),0)
TR,BR,BL,TL=[np.array(p) for p in BC['o']]
wdir=((TR-TL)+(BR-BL)); wdir/=np.linalg.norm(wdir)
for fr_ in [0.3,0.6]:
    a=TL+(BL-TL)*fr_; b=TR+(BR-TR)*fr_; mid=(a+b)/2
    print('frac',fr_,'mid',np.round(mid,1),'wdir',np.round(wdir,3))
    for t in np.arange(-30,31,1.0):
        p=mid+t*wdir
        v=cv2.getRectSubPix(im,(1,1),(float(p[0]),float(p[1])))[0,0]
        print(f'  t={t:+5.1f} xy=({p[0]:.1f},{p[1]:.1f}) BGR={np.round(v).astype(int)} B-R={v[0]-v[2]:+.0f}')
