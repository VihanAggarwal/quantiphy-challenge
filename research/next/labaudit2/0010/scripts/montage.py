import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
for r in ['','s','X']:
    fr=frames(r)
    sel=[0,7,8,14,15,16,24,36,48]
    tiles=[cv2.resize(fr[i],(640,360)) for i in sel]
    for t,i in zip(tiles,sel): cv2.putText(t,str(i),(10,30),0,1,(0,255,255),2)
    rows=[np.hstack(tiles[j:j+3]) for j in range(0,9,3)]
    cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/labaudit2/0010/img/montage_{r or "o"}.jpg',np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,80])
