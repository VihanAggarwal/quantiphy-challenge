import cv2, numpy as np, sys
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0020.mp4'
frames=[int(a) for a in sys.argv[1].split(',')]; X0,Y0,X1,Y1=map(int,sys.argv[2].split(',')); sc=float(sys.argv[3]); out=sys.argv[4]
cap=cv2.VideoCapture(p); F=[]
while True:
    ok,im=cap.read()
    if not ok: break
    F.append(im)
small=lambda im: cv2.resize(im,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
ref=cv2.cvtColor(small(F[18]),cv2.COLOR_BGR2GRAY).astype(np.float32)
emask=np.zeros_like(ref,np.uint8); emask[:, :1000]=255; emask[1050:, :]=255
tiles=[]
for i in frames:
    g=cv2.cvtColor(small(F[i]),cv2.COLOR_BGR2GRAY).astype(np.float32)
    w=np.eye(2,3,dtype=np.float32)
    cc,w=cv2.findTransformECC(ref,g,w,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,100,1e-5),emask,5)
    w[:,2]*=2
    al=cv2.warpAffine(F[i],w,(4096,2160),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP)
    d=np.abs(al.astype(np.float32)-F[18].astype(np.float32)).sum(2)[Y0:Y1,X0:X1]
    m=cv2.cvtColor(np.clip(d*1.5,0,255).astype(np.uint8),cv2.COLOR_GRAY2BGR)
    m=cv2.resize(m,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
    g_=int(sys.argv[5]) if len(sys.argv)>5 else 50
    for gy in range((Y0//g_+1)*g_,Y1,g_):
        Y=int((gy-Y0)*sc); cv2.line(m,(0,Y),(m.shape[1],Y),(0,200,255) if gy%(2*g_)==0 else (0,90,120),1)
        if gy%(2*g_)==0: cv2.putText(m,str(gy),(2,Y-2),0,0.4,(0,0,255),1)
    for gx in range((X0//g_+1)*g_,X1,g_):
        X=int((gx-X0)*sc); cv2.line(m,(X,0),(X,m.shape[0]),(0,200,255) if gx%(2*g_)==0 else (0,90,120),1)
        if gx%(2*g_)==0: cv2.putText(m,str(gx),(X+2,12),0,0.35,(0,0,255),1)
    cv2.putText(m,'f%d'%i,(5,m.shape[0]-8),0,0.7,(0,0,255),2)
    tiles.append(m)
cv2.imwrite(out,np.hstack(tiles))
