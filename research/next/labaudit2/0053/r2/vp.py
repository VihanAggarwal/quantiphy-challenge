import cv2,numpy as np
f=711.;cx=640.;cy=360.
K=np.array([[f,0,cx],[0,f,cy],[0,0,1]])
def hl(x1,y1,x2,y2): return np.cross([x1,y1,1.],[x2,y2,1.])
def vp_ls(lines):
    # least squares VP: minimize sum (l.v)^2 with normalized lines
    A=[]
    for (x1,y1,x2,y2) in lines:
        l=hl(x1,y1,x2,y2); l/=np.hypot(l[0],l[1]); A.append(l)
    A=np.array(A); _,_,vt=np.linalg.svd(A); v=vt[-1]; return v/v[2], A
# floor line A (right wall base) and B (left wall base)
A_lines=[(710.8,97.5,804.9,165.7),(806.6,168.5,1090.7,370.5),(1090.2,370.4,1279.6,509.8)]
B_lines=[(116.5,710.7,120.5,605.6),(120,604.5,123.5,478),(124.6,476.9,127.5,360.6),(128.4,359.4,130.1,255.6)]
# fit single line each
def fitline(segs):
    pts=np.array([[s[0],s[1]] for s in segs]+[[s[2],s[3]] for s in segs])
    vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_L2,0,0.01,0.01).ravel()
    return hl(x0,y0,x0+vx,y0+vy)
la=fitline(A_lines); lb=fitline(B_lines)
vpA=np.cross(la,lb); vpA/=vpA[2]; print('VP A (corridor dir)',vpA)
# vertical seams
V_lines=[(1002.4,260.9,1129.6,3.2),(1137.9,0.5,1033.6,212.7),(1278.7,111,1118.1,358.9),(1118.1,346.9,1206.8,211),(1208,209.3,1263.4,122.5)]
vpV,_=vp_ls(V_lines); print('VP vertical',vpV)
nV=np.linalg.solve(K,vpV); nV/=np.linalg.norm(nV)
if nV[1]>0: nV=-nV  # up points to -y
print('up from vertical VP',nV, 'pitch deg',np.degrees(np.arcsin(-nV[2])) )
# carpet streaks: lines with angle 150-175 and on floor region y>300
med=cv2.imread('median0053.png'); g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY)
L=cv2.createLineSegmentDetector().detect(g)[0].reshape(-1,4)
ln=np.hypot(L[:,2]-L[:,0],L[:,3]-L[:,1]); ang=np.degrees(np.arctan2(L[:,3]-L[:,1],L[:,2]-L[:,0]))%180
sel=(ln>40)&(ang>150)&(ang<178)&(np.minimum(L[:,1],L[:,3])>280)&(np.maximum(L[:,0],L[:,2])<1000)&(np.minimum(L[:,0],L[:,2])>150)
S=L[sel]; print('n streaks',len(S))
vpC,Al=vp_ls(S); print('VP carpet',vpC)
res=np.abs(Al@vpC)/1; print('resid px median', np.median(res))
hor=np.cross(vpA,vpC); 
n=K.T@hor; n/=np.linalg.norm(n)
if n[1]>0: n=-n
print('up from horizon',n,'pitch',np.degrees(np.arcsin(-n[2])))
print('angle between two normals deg',np.degrees(np.arccos(abs(n@nV))))
np.save('normals.npy',np.array([n,nV]))
