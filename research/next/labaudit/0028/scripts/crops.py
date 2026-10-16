import cv2, numpy as np
out='/home/user/quantiphy-challenge/research/next/labaudit/0028/frames'
def strip(render, idx, x0,y0,x1,y1, scale, name):
    ims=[]
    for i in idx:
        f=cv2.imread(f'{out}/{render}_{i:02d}.png')[y0:y1,x0:x1]
        f=cv2.resize(f,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
        cv2.putText(f,str(i),(3,18),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        ims.append(f)
    cv2.imwrite(name,np.hstack(ims))
strip('captured_0028x', range(18,30), 680,270,800,520, 1.5, 'crop_x_18_29.png')
strip('captured_0028x', range(30,42), 700,270,820,520, 1.5, 'crop_x_30_41.png')
strip('captured_0028', range(18,30), 640,250,840,520, 1.0, 'crop_o_18_29.png')
