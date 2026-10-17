import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0020.mp4'
cap=cv2.VideoCapture(p); F=[]
while True:
    ok,im=cap.read()
    if not ok: break
    F.append(cv2.resize(im,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA))
ref=cv2.cvtColor(F[18],cv2.COLOR_BGR2GRAY).astype(np.float32)
H,W=ref.shape
emask=np.zeros_like(ref,np.uint8); emask[:, :1000]=255; emask[1050:, :]=255
out=[]
for i in range(0,18):
    g=cv2.cvtColor(F[i],cv2.COLOR_BGR2GRAY).astype(np.float32)
    w=np.eye(2,3,dtype=np.float32)
    cc,w=cv2.findTransformECC(ref,g,w,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,100,1e-5),emask,5)
    al=cv2.warpAffine(F[i],w,(W,H),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP)
    d=np.abs(al.astype(np.float32)-F[18].astype(np.float32)).sum(2)
    sub=d[0:1000,1150:1500]
    m=(sub>90).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    comp=(lab==k)
    rows=np.nonzero(comp.sum(1)>=8)[0]
    yb=rows.max()
    xs=np.nonzero(comp[yb-3:yb+1].any(0))[0]
    out.append((i,(yb)*2,(xs.mean()+1150)*2))
    print(i,'lowest y %d x %.0f'%(yb*2,(xs.mean()+1150)*2))
o=np.array(out)
print('disp per frame (px full res):')
for j in range(len(o)-1):
    dx=o[j+1,2]-o[j,2]; dy=o[j+1,1]-o[j,1]
    print('%d->%d dy %.0f dx %.0f |d| %.0f  -> cm/s %.1f'%(o[j,0],o[j+1,0],dy,dx,np.hypot(dx,dy),np.hypot(dx,dy)*11.7/620*25))
