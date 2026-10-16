import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
E=np.load(d+'edges.npy',allow_pickle=True).item()
pb,pl,pr=E['pb'],E['pl'],E['pr']
med=cv2.imread(d+'median_x.png')
g=cv2.GaussianBlur(cv2.cvtColor(med,cv2.COLOR_BGR2GRAY).astype(float),(3,3),0)
gy=np.diff(g,axis=0)
fx=[];fy=[]
for x in range(490,945):
    seg=gy[470:505,x]; k=np.argmin(seg)
    if 0<k<len(seg)-1:
        a,b,c=seg[k-1],seg[k],seg[k+1]; off=0.5*(a-c)/(a-2*b+c)
    else: off=0
    fx.append(x); fy.append(470+k+off+0.5)
fx=np.array(fx);fy=np.array(fy)
pf=np.polyfit(fx,fy,1); res=fy-np.polyval(pf,fx); keep=np.abs(res)<1.5
pf=np.polyfit(fx[keep],fy[keep],1); print('front',pf,np.std(fy[keep]-np.polyval(pf,fx[keep])),keep.mean())
def inter_xy(py,px):  # y=py0*x+py1 ; x=px0*y+px1
    # x = px0*(py0 x + py1)+px1
    x=(px0:=px[0])*py[1]+px[1]; x/= (1-px[0]*py[0]); return np.array([x,py[0]*x+py[1]])
BL=inter_xy(pb,pl); BR=inter_xy(pb,pr); FL=inter_xy(pf,pl); FR=inter_xy(pf,pr)
print('BL',BL,'BR',BR,'FL',FL,'FR',FR)
C=dict(BL=BL,BR=BR,FL=FL,FR=FR)
json.dump({k:v.tolist() for k,v in C.items()},open(d+'corners.json','w'))
for f in [690,700,711,720,730]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); Ki=np.linalg.inv(K)
    h=lambda p: np.array([p[0],p[1],1.])
    def vp(a,b,c,dd):
        l1=np.cross(h(a),h(b)); l2=np.cross(h(c),h(dd)); v=np.cross(l1,l2); return v
    v1=Ki@vp(BL,FL,BR,FR); v2=Ki@vp(BL,BR,FL,FR)
    v1/=np.linalg.norm(v1); v2/=np.linalg.norm(v2)
    n=np.cross(v1,v2); n/=np.linalg.norm(n)
    if n[1]>0: n=-n   # normal pointing up (y down in image => up is -y)
    # plane n.X = -h  (camera above table: plane below camera)
    rays={k:Ki@h(v) for k,v in C.items()}
    # set plane n.X = c with c from unit (c=1) then scale later
    P={k: r/(n@r) for k,r in rays.items()}  # points with n.X=1
    Wb=np.linalg.norm(P['BR']-P['BL']); Wf=np.linalg.norm(P['FR']-P['FL']); Dl=np.linalg.norm(P['FL']-P['BL']); Dr=np.linalg.norm(P['FR']-P['BR'])
    print('f',f,'cos(v1,v2)=%.4f'%(v1@v2),'n',n.round(4),'W/D=%.3f'%((Wb+Wf)/(Dl+Dr)),'Wb/Wf %.3f Dl/Dr %.3f'%(Wb/Wf,Dl/Dr))
    if f==711:
        np.save(d+'plane711.npy',dict(n=n,P=P))
        # scale such that W=76 -> camera height
        s=0.76/((Wb+Wf)/2); print('  if long side=76: cam height above top %.3f m, D=%.3f'%(s*1,s*(Dl+Dr)/2))
        s2=0.603/((Dl+Dr)/2); print('  if short side=60.3: cam height %.3f m, W=%.3f'%(s2,s2*(Wb+Wf)/2))
        for k in P: print('  ',k,'range',np.linalg.norm(P[k])*s)
