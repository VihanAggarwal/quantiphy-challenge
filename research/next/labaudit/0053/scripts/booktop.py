import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
from models import M
# edge-based: fit lines to strong gradient points along each side in o-render median
fr=[cv2.imread(f'frames/o_{n:02d}.png').astype(np.float32) for n in range(0,48,2)]
med=np.median(np.stack(fr),0); g=cv2.GaussianBlur(med.mean(2),(0,0),0.8)
gx=cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
quad_sil=np.load('book_quad.npy')   # TR, TL, BL, BR (silhouette)
def refine_side(p0,p1,inner_shift=0.0,search=5):
    d=p1-p0; L=np.linalg.norm(d); d/=L; nr=np.array([-d[1],d[0]])
    # ensure normal points outward from book centre
    c=np.array([666.4,617.9]); 
    if (p0+p1)/2@nr - c@nr <0: nr=-nr
    pts=[]
    for t in np.linspace(0.2,0.8,25):
        base=p0+t*L*d
        best=None
        for s in np.arange(-search,search+0.01,0.25):
            q=base+(s-inner_shift)*nr
            x,y=q
            gv=np.array([cv2.getRectSubPix(gx,(1,1),(float(x),float(y)))[0,0],cv2.getRectSubPix(gy,(1,1),(float(x),float(y)))[0,0]])
            val=-(gv@nr)  # bright inside -> dark outside: gradient along outward normal negative
            if best is None or val>best[0]: best=(val,q)
        pts.append(best[1])
    pts=np.array(pts); mu=pts.mean(0); U,S,Vt=np.linalg.svd(pts-mu); return mu,Vt[0]
sides=[]
for j in range(4):
    sides.append(refine_side(quad_sil[j],quad_sil[(j+1)%4]))
corn=[]
for j in range(4):
    (m1,d1),(m2,d2)=sides[j-1],sides[j]
    t=np.linalg.solve(np.c_[d1,-d2],m2-m1); corn.append(m1+t[0]*d1)
corn=np.array(corn); print('edge-refined outer corners (TR,TL,BL,BR)',np.round(corn,1).tolist())
manual=np.array([[667,577.6],[633,588],[661,651],[701,635]],float)  # top face by eye
for nm,Q2 in [('silhouette',quad_sil),('edge-outer',corn),('top-face by eye',manual)]:
    for m in M[:2]:
        Pb=m.P(666.4,617.9,2.082); d0=Pb@m.dn
        Q=np.array([m.ray(u,v)*d0/(m.ray(u,v)@m.dn) for u,v in Q2])
        e=[np.linalg.norm(Q[(j+1)%4]-Q[j]) for j in range(4)]
        ang=[np.degrees(np.arccos((Q[j-1]-Q[j])@(Q[(j+1)%4]-Q[j])/np.linalg.norm(Q[j-1]-Q[j])/np.linalg.norm(Q[(j+1)%4]-Q[j]))) for j in range(4)]
        print('%-16s %-24s width %.1f/%.1f length %.1f/%.1f angles %s'%(nm,m.name,e[0]*100,e[2]*100,e[1]*100,e[3]*100,np.round(ang,0)))
