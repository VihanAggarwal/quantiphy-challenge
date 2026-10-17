import cv2, numpy as np, sys
p = sys.argv[1]
cap = cv2.VideoCapture(p)
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg = np.median(np.stack(fr[36:]+fr[1:12]),axis=0)
noise = np.std(np.stack(fr[36:]+fr[1:12]),axis=0)
print('noise median',np.median(noise))
for i in range(14,35,2):
    d = cv2.GaussianBlur(fr[i]-bg,(21,21),0)
    pos = fr[i]-bg>15
    pos = cv2.dilate(pos.astype(np.uint8),np.ones((61,61),np.uint8))>0
    d[pos]=0
    d[230:360,1690:1830]=0
    # downsample to 40px blocks
    H,W=d.shape
    b=d[:H//40*40,:W//40*40].reshape(H//40,40,W//40,40).mean(axis=(1,3))
    idx=np.argsort(b.ravel())[:3]
    print(i,[(int(k//b.shape[1])*40,int(k%b.shape[1])*40,round(float(b.ravel()[k]),2)) for k in idx], 'max', [(int(k//b.shape[1])*40,int(k%b.shape[1])*40,round(float(b.ravel()[k]),2)) for k in np.argsort(-b.ravel())[:2]])
