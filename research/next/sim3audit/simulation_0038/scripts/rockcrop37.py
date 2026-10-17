import cv2, numpy as np
a=cv2.imread('frames/simulation_0037_f024.png'); b=cv2.imread('frames/simulation_0037_segmented_f024.png')
for name,(x0,x1,y0,y1) in {'L':(0,260,570,740),'R':(480,740,620,760)}.items():
    ca=a[y0:y1,x0:x1]; cb=b[y0:y1,x0:x1]
    s=4
    ca=cv2.resize(ca,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST); cb=cv2.resize(cb,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
    for c in (ca,cb):
        for y in range(0,c.shape[0],40): c[y,:]=(0,0,255) if ((y//40)%5==0) else (180,180,255)
    cv2.imwrite(f'frames/rock37_{name}.png',np.vstack([ca,cb]))
