import cv2, numpy as np
from edgefit import edge_line, inter
f=711.;cx=640.;cy=360.
img=cv2.imread('median_bg.png').astype(np.float32)
blu=img[...,0]-img[...,2]  # B-R
blu=cv2.GaussianBlur(blu,(3,3),0)
cv2.imwrite('bag_blueness.png',np.clip(cv2.resize(blu[285:380,760:905],None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)*3,0,255).astype(np.uint8))
L=(771,315); T=(821,295.5); R=(895,347); B=(843,372)
out={}
for frac in [0.5]:
    lt,p1,r1=edge_line(blu,L,T,trim=(0.25,0.8),half=7,frac=frac)
    tr,p2,r2=edge_line(blu,T,R,trim=(0.1,0.25),half=7,frac=frac)   # avoid handle attach region
    tr2,p2b,r2b=edge_line(blu,T,R,trim=(0.1,0.95),half=7,frac=frac)
    rb,p3,r3=edge_line(blu,R,B,trim=(0.2,0.8),half=7,frac=frac)
    bl,p4,r4=edge_line(blu,B,L,trim=(0.15,0.85),half=7,frac=frac)
    for nm,(pp,rr) in {'LT':(p1,r1),'TR(short)':(p2,r2),'TR(full)':(p2b,r2b),'RB':(p3,r3),'BL':(p4,r4)}.items():
        print(nm,'n',len(pp),'rms',round(float(np.sqrt(np.mean(rr**2))),2),'maxabs',round(float(np.max(np.abs(rr))),2))
    for trl,lab in [(tr,'short'),(tr2,'full')]:
        C=[inter(bl,lt),inter(lt,trl),inter(trl,rb),inter(rb,bl)]
        print('TR',lab,'corners L,T,R,B',[np.round(c,1).tolist() for c in C])
        out[lab]=np.array(C)
np.save('bag_corners_full.npy',out['full']); np.save('bag_corners_short.npy',out['short'])
