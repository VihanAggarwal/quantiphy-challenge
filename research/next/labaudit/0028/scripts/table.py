import cv2, numpy as np
out='/home/user/quantiphy-challenge/research/next/labaudit/0028/frames'
f=cv2.imread(f'{out}/captured_0028x_10.png').astype(int)
hsv=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(int)
m=(f.sum(2)>120)
m[:400,:]=False; m[530:,:]=False
# column-wise top edge of table and bottom of face
for x in range(440,1000,20):
    col=np.nonzero(m[:,x])[0]
    if len(col): print(x, col.min(), col.max())
