import cv2, numpy as np
fr='/home/user/quantiphy-challenge/research/next/labaudit/0029/frames/'
f=cv2.imread(fr+'rx_48.png').astype(float)
m=(f.sum(2)>60).astype(np.uint8)
# top boundary per column
for x in range(200,1160,40):
    col=np.where(m[300:700,x])[0]
    if len(col): print(x, 300+col[0], 300+col[-1])
# leftmost / rightmost per row
for y in range(440,600,8):
    row=np.where(m[y,:])[0]
    if len(row): print('y',y,row[0],row[-1])
