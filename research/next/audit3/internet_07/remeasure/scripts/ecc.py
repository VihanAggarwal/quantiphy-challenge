from load import load
import numpy as np, cv2, json
fr=load()
N=len(fr)
bg=np.median(np.stack(fr[96:114:2]),axis=0).astype(np.float32)
box={}
for i in range(N):
    d=np.abs(fr[i].astype(np.float32)-bg)[680:980]
    col=(d>50).sum(0); xs=np.where(col>100)[0]
    if len(xs)>50: box[i]=(int(xs.min()),int(xs.max()))
ref=100
T=fr[ref].astype(np.float32)
out={}
for i in range(30,N):
    m=np.zeros((1080,1920),np.uint8); m[588:800,:]=255
    if i in box:
        x0,x1=box[i]; m[:,max(0,x0-120):min(1920,x1+330)]=0
    W=np.eye(2,3,dtype=np.float32)
    try:
        cc,W=cv2.findTransformECC(T,fr[i].astype(np.float32),W,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,200,1e-6),m,5)
    except cv2.error as e:
        cc=np.nan
    # W maps template coords -> frame coords: x_i = W @ [x_ref,y_ref,1]
    out[i]=W.tolist()
    xL=W@np.array([410,620,1]); xR=W@np.array([1580,620,1]); xC=W@np.array([960,800,1])
    print(i,'cc %.3f'%cc,'L %+.2f %+.2f'%tuple(xL-[410,620]),'R %+.2f %+.2f'%tuple(xR-[1580,620]),'C %+.2f %+.2f'%tuple(xC-[960,800]),'sx %.5f'%W[0,0])
json.dump({'box':box,'W':out},open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/ecc.json','w'))
