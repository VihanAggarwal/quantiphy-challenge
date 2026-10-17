import numpy as np, sys, cv2
from masks import load, mask
c=sys.argv[1]; Vs=[np.load(f'V_{c}.npy')]+[np.array([float(a) for a in s.split(',')]) for s in sys.argv[2:]]
fr=load(c)
tr=np.load(f'tracks_{c}.npy').astype(np.float64)[:,1:]
T=tr.shape[1]; t=np.arange(T).astype(float)
ngrid=np.exp(np.linspace(np.log(50),np.log(8000),800))
S=ngrid[:,None]/(ngrid[:,None]+t[None,:]); ss=(S*S).sum(1)
FPS=24.0; VEL=1.67
masks={k:mask(fr[k])[0] for k in (1,12,36,48,52,56,60,71)}
for V in Vs:
    X=tr-V
    A=np.einsum('gt,ntk->ngk',S,X)/ss[None,:,None]
    res=(X**2).sum((1,2))[:,None]-(A**2).sum(2)*ss[None,:]
    g=np.argmin(res,1); rms=np.sqrt(res[np.arange(len(tr)),g]/T); n=ngrid[g]
    good=(rms<1.5)
    print('V',V,'good tracks',good.sum(),'median rms %.2f'%np.median(rms[good]))
    for k in sorted(masks):
        m=masks[k]
        cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        P=max(cnts,key=len).reshape(-1,2).astype(float)
        d=P-V; r=np.linalg.norm(d,axis=1); th=np.degrees(np.arctan2(d[:,1],d[:,0]))
        # head tracks at frame k (video frame k -> index k-1)
        xk=tr[good,k-1]; dk=xk-V; rk=np.linalg.norm(dk,axis=1); thk=np.degrees(np.arctan2(dk[:,1],dk[:,0]))
        tau=(n[good]+k-1)/FPS
        tr_prod=tau*rk  # = f D / v_z  (s*px)
        # snout: contour point with min r (farthest along motion)
        i=np.argmin(r); th_s=th[i]; r_s=r[i]
        near=np.abs(thk-th_s)<1.0
        if near.sum()<3: near=np.argsort(np.abs(thk-th_s))[:8]
        K=np.median(tr_prod[near])
        tau_s=K/r_s
        lam_s=VEL*tau_s   # axial coord (+ const) of snout
        # every contour point's axial coord assuming same D as snout line
        lam=VEL*K/r
        # rear extreme: max lam among contour points; also both fluke tip extremes on either side of axis
        j=np.argmin(lam)
        side=th>th_s
        jl=np.argmin(np.where(side,lam,np.inf)); jr=np.argmin(np.where(~side,lam,np.inf))
        L_any=lam_s-lam[j]
        L_tips=lam_s-0.5*(lam[jl]+lam[jr])
        print(f' frame {k:2d} snout ({P[i,0]:.0f},{P[i,1]:.0f}) th {th_s:.1f} tau_s {tau_s:.2f}s  Kspread {np.std(tr_prod[near])/K*100:.1f}%  '
              f'rearmost ({P[j,0]:.0f},{P[j,1]:.0f}) L={L_any:.2f}  tipL ({P[jl,0]:.0f},{P[jl,1]:.0f}) tipR ({P[jr,0]:.0f},{P[jr,1]:.0f}) Ltips={L_tips:.2f}  maxy {P[:,1].max():.0f}')
