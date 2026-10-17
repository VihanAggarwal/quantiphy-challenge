import numpy as np
from recon import fitq, E
# estimate effective time per frame: for each track, 1/rho = a + b*t_i ; jointly solve t_i (frame times) with t_1=1,t_71=71 fixed
for c in ['0303','0305','0307']:
    P=np.load(f'tracks_{c}.npy')
    T=[t for t in fitq(P,minlen=60) if t['res']<1.0]
    # per-track normalized: r_i = (1/rho_i - a)/b  -> estimated time of frame i
    est={}
    for t in T:
        rho=np.linalg.norm(t['xy']-E,axis=1); inv=1/rho
        A=np.c_[np.ones(len(t['i'])),t['i']]; a,b=np.linalg.lstsq(A,inv,rcond=None)[0]
        for i,v in zip(t['i'],inv): est.setdefault(i,[]).append((v-a)/b - i)
    ii=sorted(est); dev=np.array([np.median(est[i]) for i in ii])
    print(c,len(T),'tracks; per-frame time deviation (frames):')
    print(' '.join('%d:%+.2f'%(i,d) for i,d in zip(ii,dev)))
