import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
from geo import *
def binmask(n):
    im=cv2.imread(f'frames/x_{n:02d}.png').astype(int)
    m=(~((im[...,1]>200)&(im[...,2]<80)&(im[...,0]<80))).astype(np.uint8)
    m[690:,1000:]=0
    k,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cand=[i for i in range(1,k) if st[i][4]>4000 and not (abs(cen[i][0]-986)<6 and abs(cen[i][1]-370)<6)]
    i=max(cand,key=lambda i:st[i][4]); return (lab==i)
def contact(n):
    m=binmask(n); ys,xs=np.nonzero(m)
    # lowest point along the 'down' image direction (towards vertical VP)
    out=[]
    for k in range(3):
        pass
    # use extreme in direction of vertical VP from centroid
    cx,cy=xs.mean(),ys.mean()
    d=np.array([VP_V[0]-cx,VP_V[1]-cy]); d/=np.linalg.norm(d)
    proj=(xs-cx)*d[0]+(ys-cy)*d[1]
    idx=np.argsort(proj)[-15:]
    return np.array([xs[idx].mean(),ys[idx].mean()]), np.array([cx,cy])
H=1.689; dn=DOWN_ROLL
res={}
for n in list(range(8,13))+list(range(32,37)):
    c,cc=contact(n); Pf=floor_pt(*c,H,dn,0.0); res[n]=(c,Pf)
    print(n,'contact px',np.round(c,1),'floor range %.3f'%np.linalg.norm(Pf))
for a,b in [(10,34),(9,33),(11,35),(10,33)]:
    print('disp contact n%d->n%d %.3f'%(a,b,np.linalg.norm(res[b][1]-res[a][1])))
# average-based
A=np.mean([res[n][1] for n in (9,10,11)],0); B=np.mean([res[n][1] for n in (33,34,35)],0)
print('avg 9-11 -> 33-35: %.3f (spans 1.0s nominal)'%np.linalg.norm(B-A))
