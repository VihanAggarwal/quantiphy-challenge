import numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work')
from recon import *
T=json.load(open(W+'taillights.json'))
for f in [4100,4240,4380]:
    K,Ki,D,L,U=cam(f)
    print('f',f,'D',np.round(D,4),'U',np.round(U,4),'pitch deg',np.degrees(np.arcsin(-U[2])) if False else np.degrees(np.arccos(-U[1])))
    Qs={}
    for nm in ['TLL','TLR']:
        tr={int(k):v for k,v in T[nm].items() if int(k)>=(31 if nm=='TLR' else 22)}
        Q,res=tri(tr,f); Qs[nm]=Q
        for k1,k2 in [(24,48),(23,47)]:
            P1=Q+(k1-24)/24*D; P2=Q+(k2-24)/24*D
            print(' ',nm,'res px %.2f'%res,'|Q| t1 %.3f'%np.linalg.norm(P1),'ratio %.4f'%(np.linalg.norm(P2)/np.linalg.norm(P1)),(k1,k2))
    sep=np.linalg.norm(Qs['TLL']-Qs['TLR']); print('  TL separation (V-units)',round(sep,4),' up-diff',round((Qs['TLL']-Qs['TLR'])@U,4),'D-diff',round((Qs['TLL']-Qs['TLR'])@D,4))
