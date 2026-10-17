import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
for r in ['x','']:
    fr=frames(r)
    med=np.median(np.stack(fr[:20]),axis=0).astype(np.uint8)
    cv2.imwrite(D+'img/median_%s.png'%(r or 'o'),med)
    cv2.imwrite(D+'img/median_%s_crop.png'%(r or 'o'),cv2.resize(med[380:520,420:1000],None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC))
