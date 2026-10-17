import cv2, numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/simulation_0216_segmented.mp4')
ok,f=cap.read()
m=(f.min(2)<235)
def colext(x0,x1,y0,y1):
    sub=m[y0:y1,x0:x1]; ys,xs=np.nonzero(sub)
    return x0+xs.min(),x0+xs.max(),y0+ys.min(),y0+ys.max()
# vase region (x 660-800, y 560-790), lamp region (x 1230-1460, y 490-790), TV (800-1230, 520-780)
for name,box in [('vase',(660,800,500,790)),('lamp',(1230,1460,480,790)),('TV',(800,1230,500,790))]:
    print(name,colext(*box))
# per-row extents for lamp shade
for y in range(500,600,6):
    xs=np.nonzero(m[y,1230:1460])[0]
    print('lamp row',y, (1230+xs.min(),1230+xs.max(),xs.max()-xs.min()+1) if len(xs) else '-')
for y in range(520,780,20):
    xs=np.nonzero(m[y,800:1230])[0]
    print('tv row',y,(800+xs.min(),800+xs.max(),xs.max()-xs.min()+1) if len(xs) else '-')
for x in (1000,1340,730):
    ys=np.nonzero(m[480:800,x])[0]; print('col',x,480+ys.min(),480+ys.max())
