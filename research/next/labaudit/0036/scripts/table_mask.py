import cv2, numpy as np
im=cv2.imread('frames/captured_0036x/f45.png')
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
m=((hsv[...,1]>40)|(hsv[...,2]<150)).astype(np.uint8)
m[690:,1020:]=0
cv2.imwrite('frames/x_mask.png',m*255)
# for each column, top-most table pixel; for each row, left/right extents
for y in range(430,640,5):
    xs=np.where(m[y,:1270])[0]
    print('row',y, xs.min() if len(xs) else None, xs.max() if len(xs) else None)
for x in range(180,1010,40):
    ys=np.where(m[380:700,x])[0]+380
    print('col',x, ys.min() if len(ys) else None)
