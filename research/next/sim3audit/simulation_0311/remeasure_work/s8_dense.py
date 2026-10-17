import numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work')
from recon import *
f=float(sys.argv[1]) if len(sys.argv)>1 else 4240.
T=json.load(open(W+'tracks.json'))
TL=json.load(open(W+'taillights.json'))
K,Ki,D,L,U=cam(f)
QL,_=tri({int(k):v for k,v in TL['TLL'].items() if int(k)>=22},f)
QR,_=tri({int(k):v for k,v in TL['TLR'].items() if int(k)>=31},f)
O=(QL+QR)/2
rows=[]
for i,t in T.items():
    tr={int(k):v for k,v in t.items()}
    if len(tr)<10: continue
    ks=sorted(tr); 
    if ks[-1]-ks[0]<10: continue
    Q,res=tri(tr,f)
    if res>0.6: continue
    d=Q-O
    rows.append((int(i),d@D,d@L,d@U,res,len(tr),tr[ks[len(ks)//2]][0],tr[ks[len(ks)//2]][1],ks[len(ks)//2]))
R=np.array(rows)
np.save(W+'dense_f%d.npy'%f,R)
print('n',len(R),'TL sep',np.linalg.norm(QL-QR),'TLL-TLR along L',(QL-QR)@L)
print('fwd range',R[:,1].min(),R[:,1].max(),' lat range',R[:,2].min(),R[:,2].max(),' up range',R[:,3].min(),R[:,3].max())
o=np.argsort(-R[:,3])
print('top 15 by up (id fwd lat up res n x y k)'); 
for r in R[o[:15]]: print(np.round(r,3))
print('bottom 15 by up');
for r in R[o[-15:]]: print(np.round(r,3))
