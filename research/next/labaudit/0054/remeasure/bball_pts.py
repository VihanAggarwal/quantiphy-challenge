import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from geom import *
def circfit(p):
    A=np.c_[2*p[:,0],2*p[:,1],np.ones(len(p))]; b=(p**2).sum(1)
    s=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(s[2]+s[0]**2+s[1]**2); return s[0],s[1],r
def bb(v,i,near):
    cs=comps(v,i); cs=[c for c in cs if c['bgr'][2]>c['bgr'][0]+50 and c['A']>1500]
    c=min(cs,key=lambda c: np.hypot(*(c['c']-np.array(near))))
    cnts,_=cv2.findContours(c['mask'].astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    p=max(cnts,key=len)[:,0,:].astype(float)
    p=p[(p[:,1]<715)&(p[:,0]>2)&(p[:,0]<1277)]
    full=circfit(p)
    up=circfit(p[p[:,1]<c['c'][1]])
    return c['c'],full,up
out={}
na=(312,597); nb=(753,577)
for i in range(11,31):
    try:
        ca,fa,ua=bb('ax',i,na); na=ca
    except Exception as e: ca=None
    cb,fb,ub=bb('bx',i,nb); nb=cb
    print(i,'a centroid',None if ca is None else ca.round(1),'a circ(full)',np.round(fa,1),'a circ(upper)',np.round(ua,1),'| b centroid',cb.round(1),'b circ',np.round(fb,1))
