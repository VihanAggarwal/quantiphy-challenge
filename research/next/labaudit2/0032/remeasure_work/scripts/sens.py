import numpy as np
base='/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/'
f=711.; cx=640.; cy=360.
K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]]); Ki=np.linalg.inv(K)
def ray(u,v):
    d=Ki@np.array([u,v,1.]); return d/np.linalg.norm(d)
def capidx(j): return np.where(j>=36, j+2, j+1)
tracks={}
for tag,src in (('circ_a','circ_a.npy'),('circ_ax','circ_ax.npy'),('blob_a','white_rows_0032.npy'),('blob_x','white_rows_0032x.npy')):
    C=np.load(base+src); C=C[C[:,0]>=36]; tracks[tag]=C[:,:3]
# mean track of the circle fits (true-centre estimators)
tracks['circ_mean']=(tracks['circ_a']+tracks['circ_ax'])/2
for vh in (344.0,349.5,353.0,356.0,362.0):
    # horizon line through (717.6,vh) with slope 0.00397
    lh=np.array([-0.00397,1.0,-(vh-0.00397*717.6)])
    n=K.T@lh; n/=np.linalg.norm(n)
    if n[1]<0: n=-n
    out=[]
    for tag in ('circ_mean','circ_a','circ_ax','blob_a','blob_x'):
        C=tracks[tag]; j=C[:,0]; u=C[:,1]; v=C[:,2]
        c=capidx(j); t=(c-38)/25.
        hc=137.3*(n@ray(u[0],v[0]))
        P=np.array([ray(a,b)*hc/(n@ray(a,b)) for a,b in zip(u,v)])
        # quadratic fit over all 13 frames; also linear fit over first 5 frames
        A=np.c_[np.ones_like(t),t,t**2]; co,_,_,_=np.linalg.lstsq(A,P,rcond=None)
        p0=co[0]; p1=co[0]+co[1]/25+co[2]/625
        fdq=np.linalg.norm(p1-p0)*25
        A5=np.c_[np.ones(5),t[:5]]; c5,_,_,_=np.linalg.lstsq(A5,P[:5],rcond=None)
        lin5=np.linalg.norm(c5[1])
        A13=np.c_[np.ones_like(t),t]; c13,_,_,_=np.linalg.lstsq(A13,P,rcond=None)
        out.append('%s q38=%.1f lin5=%.1f lin13=%.1f'%(tag,fdq,lin5,np.linalg.norm(c13[1])))
    print('v_h=%.1f  hc=%.2f |'%(vh,hc),' | '.join(out))
