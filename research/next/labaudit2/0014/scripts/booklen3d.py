import numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from tplane import *
BC=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/book_corners.json'))
f=711.; n,cP,_,_,_=pose(f); nv,_=plane_from_vps(f); nv=nv if nv@n>0 else -nv
for r in ['o','s','x']:
    TR,BR,BL,TL=[np.array(p) for p in BC[r]]
    ldir=((BL-TL)+(BR-TR)); ldir/=np.linalg.norm(ldir)
    wdir=((TR-TL)+(BR-BL)); wdir/=np.linalg.norm(wdir)
    out=[]
    for fw in [0.3,0.5,0.7]:
        a=TL+(TR-TL)*fw; b=BL+(BR-BL)*fw; mid=(a+b)/2
        for (tf,tn,lab) in [(-23.5,21.7,'cover'),(-24.5,22.5,'cover+outline'),(-23.5,28.5,'to page-block bottom')]:
            for N,cn in [(n,'PnP-n'),(nv,'VP-n')]:
                A=inter(*(mid+tf*ldir),N,0.895-0.0146,f)
                if lab=='to page-block bottom':
                    B=inter(*(mid+tn*ldir),N,0.895,f)
                else:
                    B=inter(*(mid+tn*ldir),N,0.895-0.0146,f)
                sd=np.linalg.norm(bp(*(mid+tf*ldir),1.665)-bp(*(mid+tn*ldir),1.665))
                out.append((fw,lab,cn,100*np.linalg.norm(A-B),100*sd))
    import collections
    agg=collections.defaultdict(list)
    for fw,lab,cn,L,sd in out: agg[(lab,cn)].append(L); agg[(lab,'single-depth')].append(sd)
    print(r, {f'{k[0]}|{k[1]}':round(float(np.mean(v)),2) for k,v in agg.items()})
