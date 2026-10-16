import numpy as np
f=711.; cx=640.; cy=360.
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/normal.npy')
C=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/corners_captured_0008_10.npy')
def ray(p):
    r=np.array([p[0]-cx,p[1]-cy,f]); return r/np.linalg.norm(r)
def pix(X): return np.array([f*X[0]/X[2]+cx,f*X[1]/X[2]+cy])
R=0.116
import cv2
cont=C.astype(np.float32).reshape(-1,1,2)
for h in [0.849,0.855,0.86]:
  for mode in ['surf','centre']:
    add=R if mode=='surf' else 0
    B1=(1.401+add)*ray((532,157)); B15=(1.5225+add)*ray((548,305)); B12=(1.564+add)*ray((574,382))
    # desk points: pixels on table where range==1.725 (as given; desk is a surface, depth used directly)
    res=[]
    for u in np.arange(420,770,1.0):
        # solve along column for range 1.725 on plane: point on plane along ray(u,v) has range -h/(n.r)
        vs=np.arange(370,610,0.25)
        rr=np.array([-h/(n@ray((u,v))) for v in vs])
        k=np.argmin(abs(rr-1.725))
        if abs(rr[k]-1.725)<0.002 and cv2.pointPolygonTest(cont,(float(u),float(vs[k])),False)>0:
            D=1.725*ray((u,vs[k])); res.append((u,vs[k],np.linalg.norm(B1-D),np.linalg.norm(B15-D),np.linalg.norm(B12-D)))
    res=np.array(res)
    foot1=B1-(n@B1+h)*n
    print(f'h={h} {mode}: heights B1 {100*(n@B1+h):.1f} B1.5 {100*(n@B15+h):.1f} B1.2 {100*(n@B12+h):.1f}; foot1 pix {np.round(pix(foot1),1)} range {np.linalg.norm(foot1):.3f}')
    print('   desk-locus (range 1.725) u from %.0f to %.0f; d(B1,D) min %.1f max %.1f; d(B1.5,D) min %.1f max %.1f'%(res[0,0],res[-1,0],100*res[:,2].min(),100*res[:,2].max(),100*res[:,3].min(),100*res[:,3].max()))
    for row in res[::25]: print('     D pix (%.0f,%.1f): d_init %.1f d_reb %.1f d(1.2) %.1f'%(row[0],row[1],100*row[2],100*row[3],100*row[4]))
