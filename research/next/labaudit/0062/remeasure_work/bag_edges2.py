import cv2, numpy as np
from edgefit import edge_line, inter
f=711.;cx=640.;cy=360.
img=cv2.imread('median_bg.png').astype(np.float32)
blu=cv2.GaussianBlur(img[...,0]-img[...,2],(3,3),0)
L=(771,315); T=(821,295.5); R=(895,347); B=(843,372)
def trimmed(p,q,trim,half=7):
    l,pts,res=edge_line(blu,p,q,trim=trim,half=half,step=0.5)
    for it in range(5):
        keep=np.abs(res)<max(0.8,1.5*np.median(np.abs(res)))
        pts=pts[keep]
        vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_L2,0,0.01,0.01).ravel()
        l=np.cross([x0,y0,1.],[x0+vx,y0+vy,1.]); res=(np.c_[pts,np.ones(len(pts))]@l)/np.hypot(l[0],l[1])
    return l,pts,res
lt,p1,r1=trimmed(L,T,(0.2,0.85))
tr,p2,r2=trimmed(T,R,(0.08,0.95))
rb,p3,r3=trimmed(R,B,(0.15,0.85))
bl,p4,r4=trimmed(B,L,(0.1,0.9))
for nm,pp,rr in [('LT',p1,r1),('TR',p2,r2),('RB',p3,r3),('BL',p4,r4)]:
    print(nm,len(pp),'rms',round(float(np.sqrt(np.mean(rr**2))),2),'x-range',round(pp[:,0].min()),round(pp[:,0].max()))
C=np.array([inter(bl,lt),inter(lt,tr),inter(tr,rb),inter(rb,bl)])
print('corners L,T,R,B',np.round(C,1).tolist())
np.save('bag_corners_trim.npy',C)
# overlay
big=cv2.resize(cv2.imread('median_bg.png')[285:380,760:905],None,fx=6,fy=6,interpolation=cv2.INTER_CUBIC)
for k in range(4):
    a=((C[k]-[760,285])*6).astype(int); b=((C[(k+1)%4]-[760,285])*6).astype(int)
    cv2.line(big,tuple(a),tuple(b),(0,0,255),1)
for pp in (p1,p2,p3,p4):
    for q in pp: cv2.circle(big,tuple(((q-[760,285])*6).astype(int)),1,(0,255,0),-1)
cv2.imwrite('bag_fit_overlay.png',big)
