import cv2, numpy as np
im=cv2.imread('frames/simulation_0209_f029.png'); g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector(0)
L=lsd.detect(g)[0].reshape(-1,4)
x1,y1,x2,y2=L.T
ln=np.hypot(x2-x1,y2-y1); ang=np.degrees(np.arctan2(y2-y1,x2-x1))%180
print(len(L))
def fitvp(sel,name):
    S=L[sel]; w=np.hypot(S[:,2]-S[:,0],S[:,3]-S[:,1])
    # homogeneous lines
    p1=np.c_[S[:,0],S[:,1],np.ones(len(S))]; p2=np.c_[S[:,2],S[:,3],np.ones(len(S))]
    l=np.cross(p1,p2); l/=np.hypot(l[:,0],l[:,1])[:,None]
    v=None
    for it in range(5):
        A=l*w[:,None] if v is None else l*w[:,None]
        if v is None:
            _,_,Vt=np.linalg.svd(A); v=Vt[-1]
        else:
            # robust reweight by distance of midpoint-line to vp
            r=np.abs(l@v)/np.linalg.norm(v[:2]) if abs(v[2])<1e-9 else None
            vv=v/v[2] if abs(v[2])>1e-12 else v
            mid=(p1+p2)/2
            # angle residual: angle between segment and line from mid to vp
            d=vv[:2]-mid[:,:2]; seg=(p2-p1)[:,:2]
            cosang=np.abs(np.sum(d*seg,1))/np.linalg.norm(d,axis=1)/np.linalg.norm(seg,axis=1)
            res=np.degrees(np.arccos(np.clip(cosang,0,1)))
            keep=res<1.0
            A=l[keep]*w[keep,None]
            _,_,Vt=np.linalg.svd(A); v=Vt[-1]
    vv=v/v[2]
    print(name,len(S),keep.sum(),vv[:2])
    return vv, S[keep]
y_mid=(y1+y2)/2
selA=(ln>40)&(ang>168)&(ang<176.5)&(y_mid>500)
selB=(ln>30)&(ang>15)&(ang<45)&(y_mid>500)
selV=(ln>40)&(ang>86)&(ang<94)&(y_mid>650)
vA,SA=fitvp(selA,'A'); vB,SB=fitvp(selB,'B'); vV,SV=fitvp(selV,'V')
np.save('vps.npy',np.array([vA,vB,vV]))
c=np.array([1062,540])
for a,b,n in [(vA,vB,'AB'),(vA,vV,'AV'),(vB,vV,'BV')]:
    f2=-np.dot(a[:2]-c,b[:2]-c); print(n,'f=',np.sqrt(f2) if f2>0 else f2)
# orthocentre
def ortho(a,b,cc):
    a,b,cc=a[:2],b[:2],cc[:2]
    # solve (p-a).(b-cc)=0, (p-b).(a-cc)=0
    M=np.array([b-cc,a-cc]); r=np.array([a@(b-cc),b@(a-cc)])
    return np.linalg.solve(M,r)
print('ortho',ortho(vA,vB,vV))
vis=im.copy()
for S,col in [(SA,(0,0,255)),(SB,(0,255,0)),(SV,(255,0,0))]:
    for s in S: cv2.line(vis,(int(s[0]),int(s[1])),(int(s[2]),int(s[3])),col,2)
cv2.imwrite('vp_lines.png',vis)
