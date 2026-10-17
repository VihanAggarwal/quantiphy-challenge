import cv2, numpy as np, json
from geo import *
from track import cover_mask
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
res={}
for pre in ['o','x']:
    L={}
    for k in range(18,32):
        im=cv2.imread(R1+f'{pre}{k:02d}.png'); m=cover_mask(im); ys,xs=np.nonzero(m)
        P=np.c_[xs,ys].astype(float); c=P.mean(0); C=np.cov((P-c).T); w,V=np.linalg.eigh(C)
        Lmaj=np.sqrt(12*w[1]); Lmin=np.sqrt(12*w[0]); ang=np.degrees(np.arctan2(V[1,1],V[0,1]))
        # robust extent along major axis: 1st/99th percentile of projections + 1 px
        pr=(P-c)@V[:,1]; ext=np.percentile(pr,99.5)-np.percentile(pr,0.5)+1
        L[k]=(Lmaj,ext,c)
        print(pre,k,'major len (moments) %.1f, extent %.1f, minor %.1f, angle %.1f deg, cen (%.1f,%.1f)'%(Lmaj,ext,Lmin,ang,c[0],c[1]))
    res[pre]=L
    # size-based ranges anchored at 1.02 at v29
    for which,idx in [('moments',0),('extent',1)]:
        r29=1.02; r30=1.02*L[29][idx]/L[30][idx]; r28=1.02*L[29][idx]/L[28][idx]
        P30=bp(*L[29][2],r29); P31=bp(*L[30][2],r30); P29=bp(*L[28][2],r28)
        print(pre,which,'size-based r(v28)=%.4f r(v30)=%.4f : v(c30->31)=%.1f  v(c29->30)=%.1f'%(r28,r30,np.linalg.norm(P31-P30)*2500,np.linalg.norm(P30-P29)*2500))
