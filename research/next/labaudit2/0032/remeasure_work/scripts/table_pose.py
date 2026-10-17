import numpy as np, cv2
def lx(a,b): return np.array([1,-b,-a])
def ly(a,b): return np.array([-b,1,-a])
Ll=lx(1386.71,-1.9149); Lr=lx(126.54,1.6917); Lt=ly(415.13,0.0155); Lf=ly(470.90,0.02487)
def X(a,b):
    p=np.cross(a,b); return p[:2]/p[2]
C=dict(FL=X(Ll,Lf),FR=X(Lr,Lf),BR=X(Lr,Lt),BL=X(Ll,Lt))
for k,v in C.items(): print(k,np.round(v,2))
vp1=X(Ll,Lr); vp2=X(Lt,Lf); print('vp depth',vp1,'vp lateral',vp2)
for f in (600,650,711,750,800):
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    Ki=np.linalg.inv(K)
    d1=Ki@np.r_[vp1,1]; d2=Ki@np.r_[vp2,1]
    d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2)
    ang=np.degrees(np.arccos(abs(d1@d2)))
    # homography approach: object rect W (x, left->right) x L (depth)
    src=np.array([[0,0],[1,0],[1,1],[0,1]],float)  # FL,FR,BR,BL in units (x along front, y toward back)
    dst=np.array([C['FL'],C['FR'],C['BR'],C['BL']])
    H,_=cv2.findHomography(src,dst)
    M=Ki@H
    a=np.linalg.norm(M[:,0]); b=np.linalg.norm(M[:,1])
    cosang=(M[:,0]@M[:,1])/(a*b)
    # aspect: W/L = a/b   (columns scaled by W and L with same lambda)
    print('f=%d angle between VPs %.2f deg, homog col cos %.4f, W/L=%.4f'%(f,ang,cosang,a/b))
