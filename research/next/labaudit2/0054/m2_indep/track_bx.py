from common import *
import numpy as np, cv2, json
fb=frames('bx')
out=[]
for i in range(20,46):
    f=fb[i].astype(int); b,g,r=f[...,0],f[...,1],f[...,2]
    fg=(f.sum(2)>90)
    yellow=fg&(g-b>50)&(r>80)
    white=fg&(abs(r-b)<50)&(abs(g-b)<50)&(b>90)
    for name,m in (('white',white),('green',yellow)):
        m=m.astype(np.uint8); m[690:,1000:]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
        cands=[k for k in range(1,n) if 150<st[k][4]<6000 and st[k][1]<560]
        # exclude soccer ball region (lower right) and basketball (orange excluded by colour)
        cands=[k for k in cands if not (cen[k][0]>800 and cen[k][1]>450)]
        if not cands: continue
        k=max(cands,key=lambda k: st[k][4])
        ys,xs=np.nonzero(lab==k); C=np.cov(np.c_[xs,ys].T); ev,_=np.linalg.eigh(C)
        out.append(dict(i=i,obj=name,x=float(xs.mean()),y=float(ys.mean()),area=int(len(xs)),Dmin=float(4*np.sqrt(ev[0])),L=float(np.sqrt(max(0,12*(ev[1]-ev[0]))))))
        print(i,name,'(%.1f,%.1f) area=%d Dmin=%.1f L=%.1f'%(xs.mean(),ys.mean(),len(xs),4*np.sqrt(ev[0]),np.sqrt(max(0,12*(ev[1]-ev[0])))))
json.dump(out,open(OUT+'bx_track.json','w'))
