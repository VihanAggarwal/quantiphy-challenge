import numpy as np,cv2,json
tr=np.load('track_captured_0053_10.npy')
T=json.load(open('bintrack.json'))
for j in [0,4,16,22,28,34,40,47]:
    ok=~np.isnan(tr[j,:,0])
    a=tr[10][ok].astype(np.float32); b=tr[j][ok].astype(np.float32)
    M,inl=cv2.estimateAffine2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=1.0)
    A=M[:,:2]
    U,S,Vt=np.linalg.svd(A)
    sx=np.linalg.norm(A[:,0]); sy=np.linalg.norm(A[:,1])
    Ms,_=cv2.estimateAffinePartial2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=1.0)
    ss=np.hypot(Ms[0,0],Ms[1,0])
    print(f'{j:2d} inl {int(inl.sum()):3d}/{ok.sum()} sx {sx:.4f} sy {sy:.4f} sqrtdet {np.sqrt(np.linalg.det(A)):.4f} sv {S.round(4)} simil {ss:.4f}  1/sx {1/sx:.4f} 1/sqrtdet {1/np.sqrt(np.linalg.det(A)):.4f}')
