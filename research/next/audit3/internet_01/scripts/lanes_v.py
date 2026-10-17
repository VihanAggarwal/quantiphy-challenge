import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/internet_01/scripts')
from util import find_peaks
# vertical road: lane lines are vertical; profile along x of high-percentile brightness in y bands
V=sys.argv[1]; step=int(sys.argv[2]); xa,xb=map(int,sys.argv[3:5])
c=cv2.VideoCapture(V); fr=[]; i=0
while True:
    ok,im=c.read()
    if not ok: break
    if i%step==0: fr.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY))
    i+=1
bg=np.median(np.stack(fr),axis=0).astype(np.float32)
H,W=bg.shape
for y0 in range(0,H,H//6):
    band=bg[y0:y0+H//6,xa:xb]
    prof=np.percentile(band,97,axis=0)
    base=np.median(prof)
    pk,_=find_peaks(prof,height=base+30,distance=25)
    cents=[]
    for p in pk:
        lo,hi=max(0,p-5),min(len(prof),p+6)
        w=np.clip(prof[lo:hi]-base,0,None); cents.append(xa+(np.arange(lo,hi)*w).sum()/w.sum())
    print(y0,np.round(cents,1),np.round(np.diff(cents),1))
cv2.imwrite(sys.argv[5],bg.astype(np.uint8)[::4,::4])
