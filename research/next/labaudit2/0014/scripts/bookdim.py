import numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from tplane import *
BC=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/book_corners.json'))
vis=[[663.6,383.9],[681.4,427.0],[640.0,435.6],[625.7,388.4]]
f=711.
n,cP,rep,R,t=pose(f)
nv,_=plane_from_vps(f)
if nv@n<0: nv=-nv
for nname,N in [('PnP-n',n),('VP-n',nv)]:
  for cname,c in [('label c=0.895',0.895),('metric PnP c',cP)]:
    for h in [0.0146]:
      for src,cor in [('o',BC['o']),('s',BC['s']),('x',BC['x']),('visual',vis)]:
        X=[inter(*p,N,c-h,f) for p in cor]
        TR,BR,BL,TL=X
        L=(np.linalg.norm(TR-BR)+np.linalg.norm(TL-BL))/2
        W=(np.linalg.norm(TR-TL)+np.linalg.norm(BR-BL))/2
        ctr=np.mean(X,0)
        print(f'{nname:5s} {cname:15s} {src:6s} long {100*L:5.2f} short {100*W:5.2f}  centre range {np.linalg.norm(ctr):.4f}  corner angle {np.degrees(np.arccos(abs((TR-BR)@(TR-TL))/np.linalg.norm(TR-BR)/np.linalg.norm(TR-TL))):.1f}')
# single-depth (label using stated 1.665 for both ends) 
for src,cor in [('o',BC['o']),('visual',vis)]:
    TR,BR,BL,TL=[bp(*p,1.665) for p in cor]
    print('single-depth',src,'long',round(100*(np.linalg.norm(TR-BR)+np.linalg.norm(TL-BL))/2,2),'short',round(100*(np.linalg.norm(TR-TL)+np.linalg.norm(BR-BL))/2,2))
