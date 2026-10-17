import numpy as np
from masks import load, mask
# confirm same render: whale mask bbox per frame index across the three clips (0304 sky bg is cleanest; compare 0304 vs others via dark-pixel bbox)
import cv2
for k in (1,36,71):
    out=[]
    for c in ('0304','0306','0308'):
        cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{c}.mp4')
        cap.set(cv2.CAP_PROP_POS_FRAMES,k); ok,f=cap.read()
        # snout region template location: use 0304 head crop as template
        out.append(f)
    tpl=out[0][300:520,900:1250]
    locs=[]
    for f in out:
        r=cv2.matchTemplate(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)[200:700,700:1500],cv2.cvtColor(tpl,cv2.COLOR_BGR2GRAY),cv2.TM_CCOEFF_NORMED)
        _,mx,_,ml=cv2.minMaxLoc(r); locs.append((ml[0]+700-900,ml[1]+200-300,round(mx,2)))
    print('frame',k,'head-template offset vs 0304 (dx,dy,score):',locs)
