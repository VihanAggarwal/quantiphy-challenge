import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0209.mp4'); ok,im=cap.read()
im=im.astype(np.float32); b,g,r=im[:,:,0],im[:,:,1],im[:,:,2]
S=r-b
y0,y1,x0,x1=600,660,1290,1440
sub=S[y0:y1,x0:x1]
print('r-b percentiles',np.percentile(sub,[5,20,50,80,95,99]))
thr=20
for yy in range(y0,y1):
    row=S[yy,x0:x1]; idx=np.where(row>thr)[0]
    if len(idx)<3: continue
    print(yy, 'x %d..%d n=%d'%(idx[0]+x0, idx[-1]+x0, len(idx)), ''.join('#' if v>thr else ('+' if v>5 else '.') for v in row[::2]))
