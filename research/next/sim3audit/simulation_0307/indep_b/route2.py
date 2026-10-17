import numpy as np
from frame3d import axes
from sweep import E, C
# features: frame-1 pixel, q (only used to move image position to frame k)
F={'Lpod_nose':((1413,796),0.008225),'Rpod_nose':((1692,743),0.007885),
   'Lfin_top':((1378,821),0.008866),'Rfin_top':((1950,712),0.008146),
   'Lpod_rear':((1622,982),0.00895),'Rpod_rear':((1913,916),0.00856),
   'finTE_bot':((1895,985),0.00922),'finTE_mid':((1899,957),0.009255),'finTE_top':((1903,933),0.00928),
   'Lfin_bot':((1360,926),0.00884)}
pairs=[('Lpod_nose','Rpod_nose'),('Lfin_top','Rfin_top'),('Lpod_rear','Rpod_rear')]
d1=102.6664
def pos(k,frame):
    p,q=F[k]; s=(1+q)/(1+q*frame); return E+(np.array(p,float)-E)*s
def run(f,frame,verbose=False):
    V,S,U=axes(f)
    ray=lambda x: np.array([(x[0]-C[0])/f,(x[1]-C[1])/f,1.0])
    P={}; s0s=[]
    for a,b in pairs:
        ra,rb=ray(pos(a,frame)),ray(pos(b,frame))
        A=np.array([[V@rb,-(V@ra)],[U@rb,-(U@ra)]])
        u,sv,vt=np.linalg.svd(A); lr,ll=vt[-1]
        if ll<0: lr,ll=-lr,-ll
        Pa,Pb=ll*ra,lr*rb
        s0=S@(Pa+Pb)/2
        P[a],P[b]=Pa/s0,Pb/s0   # normalised so plane offset =1
        if verbose: print('  pair',a,b,'cond resid %.2e'%(sv[-1]/sv[0]))
    # on-plane points: S.P = 1
    for k in ['finTE_bot','finTE_mid','finTE_top']:
        r=ray(pos(k,frame)); P[k]=r/(S@r)
    return P,V,S,U
for f in [3550,3590,3640]:
  for N in [24,25]:
    P,V,S,U=run(f,N,verbose=(f==3590 and N==24))
    fore={k:P[k]@V for k in P}; up={k:P[k]@U for k in P}; sp={k:P[k]@S for k in P}
    front=(fore['Lpod_nose']+fore['Rpod_nose'])/2
    rear=min(fore['finTE_bot'],fore['finTE_mid'],fore['finTE_top'])
    L=front-rear
    fin=np.linalg.norm(P['Rfin_top']-P['Lfin_top'])
    # AABB centre approx: fore mid, span at plane (1), up mid between top(fin tops ~0)+0.4 and pod rear bottom
    upv=[up[k] for k in P]
    # scale: put origin at AABB centre (fore mid, plane, up from extremes incl. +0.42/-3.57 offsets scaled later) -> iterate
    sc=1.0
    for it in range(20):
        top=max(upv)+0.42/sc*0 ; bot=min(upv)
        cen=((front+rear)/2)*V+1.0*S+((up['Lfin_top']+0.42/sc + up['Lpod_rear']-0.09/sc)/2)*U
        sc=d1/np.linalg.norm(cen)
    print('f %d frame %d: length/finTop = %.4f ; scale(origin=AABBc, range=d1) -> length %.2f  finTop %.2f  pod-span %.2f'%(f,N,L/fin,L*sc,fin*sc,np.linalg.norm(P['Rpod_nose']-P['Lpod_nose'])*sc))
