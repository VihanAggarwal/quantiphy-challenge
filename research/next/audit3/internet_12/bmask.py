import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0020.mp4'
cap=cv2.VideoCapture(p); F=[]
while True:
    ok,im=cap.read()
    if not ok: break
    F.append(cv2.resize(im,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA))
ref=cv2.cvtColor(F[18],cv2.COLOR_BGR2GRAY).astype(np.float32)
H,W=ref.shape
# mask for ECC: left part of image (x<1050 half-res => <2100 full) excluding nothing moving there
emask=np.zeros_like(ref,np.uint8); emask[:, :1000]=255; emask[1050:, :]=255  # bottom area: tray/sinks static
res={}
for i in range(0,19):
    g=cv2.cvtColor(F[i],cv2.COLOR_BGR2GRAY).astype(np.float32)
    w=np.eye(2,3,dtype=np.float32)
    try:
        cc,w=cv2.findTransformECC(ref,g,w,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,100,1e-5),emask,5)
    except Exception as e: print(i,e); 
    al=cv2.warpAffine(F[i],w,(W,H),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP)
    d=np.abs(al.astype(np.float32)-F[18].astype(np.float32)).sum(2)
    res[i]=(w[0,2]*2,w[1,2]*2,d)
    print(i,'shift full-res px %.1f %.1f'%(w[0,2]*2,w[1,2]*2))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/dummy.npy',np.zeros(1))
# show diff masks for frames 8..16 in bottle column band x 2350-2900 full => 1175-1450 half
tiles=[]
for i in range(6,17,1):
    d=res[i][2][0:1000,1150:1500]
    m=np.clip(d*2,0,255).astype(np.uint8)
    m=cv2.cvtColor(m,cv2.COLOR_GRAY2BGR)
    for gy in range(0,1000,50):
        cv2.line(m,(0,gy),(m.shape[1],gy),(0,200,255) if gy%100==0 else (0,90,120),1)
        if gy%100==0: cv2.putText(m,str(gy*2),(2,gy-2),0,0.4,(0,0,255),1)
    for gx in range(1150,1500,50):
        X=gx-1150; cv2.line(m,(X,0),(X,1000),(0,200,255) if gx%100==0 else (0,90,120),1)
        if gx%100==0: cv2.putText(m,str(gx*2),(X+2,12),0,0.35,(0,0,255),1)
    cv2.putText(m,'f%d'%i,(5,990),0,0.7,(0,0,255),2)
    tiles.append(cv2.resize(m,None,fx=0.6,fy=0.6))
cv2.imwrite('bm.png',np.hstack(tiles))
