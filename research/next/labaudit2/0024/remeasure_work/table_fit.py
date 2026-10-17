import numpy as np
f=711.;cx=640;cy=360
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]);return d/np.linalg.norm(d)
def along(r,P,a):
    # t such that |t r - P| = a ; returns both roots
    b=r@P; c=P@P-a*a; d=b*b-c
    if d<0: return []
    return [b-np.sqrt(d), b+np.sqrt(d)]
Lp=(413,468);Fp=(641,576)
for Rp in [(1105,496),(1115,500),(1130,502)]:
  for a,b in [(0.603,0.760),(0.760,0.603)]:
    rL,rF,rR=ray(*Lp),ray(*Fp),ray(*Rp)
    sols=[]
    prev=None
    for tF in np.linspace(0.3,1.5,24001):
        F=tF*rF
        for tL in along(rL,F,a):
            for tR in along(rR,F,b):
                if tL<=0 or tR<=0: continue
                L=tL*rL;R=tR*rR
                c=(L-F)@(R-F)/(a*b)
                sols.append((abs(c),tF,tL,tR))
    sols.sort()
    for s in sols[:1]:
        c,tF,tL,tR=s
        L,F,R=tL*rL,tF*rF,tR*rR
        n=np.cross(L-F,R-F); n/=np.linalg.norm(n)
        print(Rp,'LF=%.3f FR=%.3f'%(a,b),'|cos|=%.4f'%c,'ranges L=%.3f F=%.3f R=%.3f'%(np.linalg.norm(L),np.linalg.norm(F),np.linalg.norm(R)),'n',np.round(n,3),'h',round(abs(n@F),3))
