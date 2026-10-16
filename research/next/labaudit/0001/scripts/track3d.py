import numpy as np, cv2
f=711.; cx=640.; cy=360.; r=0.0335
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
base='/home/user/quantiphy-challenge/research/next/labaudit/0001/'
# board corners (frame 48 mask fit), bottom corners at range ~0.884, top at ~1.136
pl=np.array([-2.31534091e-01,6.51616477e+02]); pr=np.array([1.03442513e-01,6.84195744e+02])
topy=353.5; boty=493.0
BL=0.884*ray(np.polyval(pl,boty),boty); BR=0.884*ray(np.polyval(pr,boty),boty)
TL=1.136*ray(np.polyval(pl,topy),topy); TR=1.136*ray(np.polyval(pr,topy),topy)
# plane fit through 4 corners
P=np.stack([BL,BR,TL,TR]); c0=P.mean(0)
u,s,vt=np.linalg.svd(P-c0); n=vt[2]
if n[2]>0: n=-n   # normal toward camera
print('plane normal',n,'residuals',(P-c0)@n)
up=(TL+TR)/2-(BL+BR)/2; L=np.linalg.norm(up); up/=L
print('slope length (corner mids)',L,'incline vs cam-horizontal deg',np.degrees(np.arcsin(-up[1])))
# track ball centroid with tighter yellow mask
def ball(i):
    im=cv2.imread(base+'frames/f%02d.png'%i)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>20)&(hsv[...,0]<40)&(hsv[...,1]>100)&(hsv[...,2]>120)).astype(np.uint8)
    m[690:,1000:]=0
    n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    return cen[k], (x,y,w,h)
Cs={}
for i in list(range(0,1))+list(range(26,41)):
    (uu,vv),bb=ball(i)
    # intersect ray with plane offset by r along n: n.(X - c0) = r
    d=ray(uu,vv); t=(r+n@c0)/(n@d); C=t*d
    s_along=(C-(BL+BR)/2-r*n)@up
    Cs[i]=C
    print(i,'%.3f'%(i/24),'px(%.1f,%.1f) bbox w%d h%d'%(uu,vv,bb[2],bb[3]),'C=',np.round(C,4),'|C|=%.4f front=%.4f s_from_bottom=%.4f'%(np.linalg.norm(C),np.linalg.norm(C)-r,s_along), ' size-range=%.3f'%(f*0.067/bb[2]))
# t=0 ball: from label depth
(uu,vv),bb=ball(0)
C0s=1.1075*ray(uu,vv); C0c=(1.1075+r)*ray(uu,vv)
print('t0 surface-pt',C0s,'centre',C0c)
for lab_r in [0.912]:
    for i in [35,36,37]:
        (uu,vv),bb=ball(i)
        S=lab_r*ray(uu,vv)
        print('disp 0->frame',i,'surface-label', np.linalg.norm(S-C0s), ' plane-route centre-to-centre', np.linalg.norm(Cs[i]-C0c))
k=sorted(Cs)
for a,b in zip(k[:-1],k[1:]):
    print(a,'->',b,'speed cm/s %.1f'%(np.linalg.norm(Cs[b]-Cs[a])*24*100))
