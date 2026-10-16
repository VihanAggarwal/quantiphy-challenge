import numpy as np
f=711.; K=np.array([[f,0,640.],[0,f,360.],[0,0,1]]); Ki=np.linalg.inv(K)
C=np.load('scripts/corners.npy')  # FL FR BL BR (pixels, homog)
FL,FR,BL,BR=C
def line(a,b): return np.cross(a,b)
lL=line(FL,BL); lR=line(FR,BR); lF=line(FL,FR); lB=line(BL,BR)
v1=np.cross(lL,lR); d1=Ki@v1; d1/=np.linalg.norm(d1)
if d1[2]<0: d1=-d1
for nm,l in [('front',lF),('back',lB)]:
    mF=K.T@l; mF/=np.linalg.norm(mF)
    d2=np.cross(mF,d1); d2/=np.linalg.norm(d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    if n[1]<0: n=-n
    def bp(p,h): r=Ki@p; return r*h/(n@r)
    for h in [0.174,0.18,0.185]:
        P=[bp(p,h) for p in C]
        fr=np.linalg.norm(P[1]-P[0]); bk=np.linalg.norm(P[3]-P[2]); le=np.linalg.norm(P[2]-P[0]); ri=np.linalg.norm(P[3]-P[1])
        print(nm,'n',np.round(n,4),'h',h,'front %.3f back %.3f left %.3f right %.3f ratio %.3f'%(fr,bk,le,ri,(le+ri)/(fr+bk)))
