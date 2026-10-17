import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0055.mp4')
frames=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frames.append(f)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames]
win=cv2.createHanningWindow((1920,1080),cv2.CV_32F)
acc=np.zeros((1080,1920),np.float32)
dr=[]
for i in range(0,len(frames)-5,5):
    (dx,dy),r=cv2.phaseCorrelate(g[i],g[i+5],win)
    dr.append((i,round(dx,2),round(dy,2)))
    M=np.float32([[1,0,-dx],[0,1,-dy]])
    w=cv2.warpAffine(g[i+5],M,(1920,1080),borderMode=cv2.BORDER_REPLICATE)
    d=np.abs(w-g[i]); acc=np.maximum(acc,(d>35).astype(np.float32)*(i+5))
print(dr)
vis=frames[37].copy()
mask=acc>0
mask=cv2.morphologyEx(mask.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
vis[mask]=(0,0,255)
cv2.imwrite('mot55.png',cv2.resize(vis,(1280,720)))
