import cv2, numpy as np
from rectify import topview, n, f, cx, cy, plane_basis
# bag mask from x render: median over all frames (static object)
xs=np.stack([cv2.imread('frames/x_%02d.png'%i) for i in range(0,49,2)])
med=np.median(xs,axis=0).astype(np.uint8)
cv2.imwrite('x_median.png',med)
hsv=cv2.cvtColor(med,cv2.COLOR_BGR2HSV)
m=(med.max(axis=2)>35).astype(np.uint8)
m[:, :740]=0; m[:260,:]=0; m[400:,:]=0
nl,lab,st,cen=cv2.connectedComponentsWithStats(m); j=1+np.argmax(st[1:,4]); m=(lab==j).astype(np.uint8)
print('bag mask bbox',st[j].tolist())
cv2.imwrite('bag_mask.png',m*255)
h=1.85; ppc=6; half=50
img=cv2.imread('frames/o_00.png')
tv=topview(img,h,(830,335),half_cm=half,ppc=ppc); cv2.imwrite('top_bag_o00.png',tv)
tm=topview(m*255,h,(830,335),half_cm=half,ppc=ppc); cv2.imwrite('top_bag_mask.png',tm)
