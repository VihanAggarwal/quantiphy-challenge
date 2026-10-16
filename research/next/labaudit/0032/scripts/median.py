import cv2, numpy as np
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
for r in ['x','o','s']:
    fr=np.stack([cv2.imread(d+'frames/%s_%02d.png'%(r,i)) for i in range(49)])
    med=np.median(fr,axis=0).astype(np.uint8)
    cv2.imwrite(d+'median_%s.png'%r,med)
med=cv2.imread(d+'median_x.png')
crop=med[380:540,420:1000]
cv2.imwrite(d+'zoom_table_x.png',cv2.resize(crop,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
