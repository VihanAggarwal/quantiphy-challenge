import cv2, numpy as np
for v in ['simulation_0073','simulation_0075']:
    bg=cv2.imread(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/bg_{v}.png').astype(float)
    for (cx,cy) in ((410,220),(410,850),(1216,844)):
        r=bg[cy-60:cy+60,cx-60:cx+60]
        ref=np.median(np.concatenate([r[:5].reshape(-1,3),r[-5:].reshape(-1,3)]),axis=0)
        d=np.abs(r-ref).sum(axis=2)
        res=[]
        for thr in (15,30,60):
            m=d>thr
            rows=np.where(m.sum(1)>=20)[0]; cols=np.where(m.sum(0)>=20)[0]
            res.append((thr,cols[-1]-cols[0]+1,rows[-1]-rows[0]+1))
        # half-level along central row/col
        L=r.mean(axis=2)
        def hl(p):
            base=np.median(np.r_[p[:8],p[-8:]]); inner=np.median(p[50:70]); h=(base+inner)/2
            s=np.sign(inner-base); q=s*(p-h)
            idx=np.where(q>0)[0]; i0=idx[0]; i1=idx[-1]
            # subpixel
            a=i0-1+ (0-q[i0-1])/(q[i0]-q[i0-1]); b=i1+ (q[i1])/(q[i1]-q[i1+1])
            return b-a
        print(v,(cx,cy),'ref',ref.round(0),res,'halfL row %.1f col %.1f'%(hl(L[60]),hl(L[:,60])))
