import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from recon import *
v=sys.argv[1] if len(sys.argv)>1 else 'ax'
tr=load(v); bb=tr['bb']; sb=tr['sb']
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
T={k:orig(k)/25.0 for k in range(49)}
Ds=float(sys.argv[2]) if len(sys.argv)>2 else 0.181
planes={}
# plane1: from 4 stated points
def interp(t,key):
    x=t*24; i0=int(np.floor(x)); a=x-i0; d0=tr[key][i0]; d1=tr[key][i0+1]
    return (1-a)*d0['cx']+a*d1['cx'],(1-a)*d0['cy']+a*d1['cy']
St=[(0.6,'sb',2.758),(0.6,'bb',2.27),(1.6,'sb',3.052),(1.6,'bb',2.412)]
pts=[]
for t,key,r in St:
    u,w=interp(t,key); P=r*ray(u,w)
    pts.append(P)
n1,c1,_=fit_plane(pts)
planes['stated4']=(n1,c1)
# plane2: joint size fit
Pb=size_track(bb,0.232); Ps=size_track(sb,Ds)
n=n1.copy()
for it in range(10):
    p2=[Pb[i] for i in range(9,49)]+[Ps[i]+(0.116-Ds/2)*n for i in sb if i>=10]
    n,c,_=fit_plane(p2)
planes['joint']=(n,c)
for name,(n,c) in planes.items():
    print(name,'n',np.round(n,3),'h',round(float(n@c),3))
def tracks(name):
    if name=='size': return Pb,Ps
    n,c=planes[name]
    # plane through c is basketball centre plane (stated4 mixes; treat as average-ball plane)
    return plane_track(bb,n,c,0.0), plane_track(sb,n,c,-(0.116-Ds/2) if name=='joint' else 0.0)
def vel(P,k,w=1):
    # forward difference over w video frames, using true times
    return np.linalg.norm(P[k+w]-P[k])/(T[k+w]-T[k])
def vfit(P,k,h=2):
    ks=[j for j in range(k-h,k+h+1) if j in P]
    t=np.array([T[j] for j in ks]); X=np.array([P[j] for j in ks])
    A=np.vstack([t,np.ones_like(t)]).T
    coef=np.linalg.lstsq(A,X,rcond=None)[0]
    return np.linalg.norm(coef[0])
for name in ['size','stated4','joint']:
    B,Sc=tracks(name)
    out=[]
    for t in [0.6,1.5,1.6]:
        k=int(round(t*24))
        out.append('t=%.1f(k%d) sb fwd %.0f fit %.0f | bb fwd %.0f fit %.0f'%(t,k,vel(Sc,k)*100,vfit(Sc,k)*100,vel(B,k)*100,vfit(B,k)*100))
    # displacement 0.5-0.6
    d=[]
    for (k0,k1) in [(12,14),(12,15),(11,14)]:
        d.append('k%d-%d sb %.1f bb %.1f'%(k0,k1,100*np.linalg.norm(Sc[k1]-Sc[k0]),100*np.linalg.norm(B[k1]-B[k0])))
    print(name); print('  '+'\n  '.join(out)); print('  disp',d)
    # range at stated times
    for t,key,r in St:
        k=t*24; i0=int(k); a=k-i0; P=(B if key=='bb' else Sc)
        rr=(1-a)*np.linalg.norm(P[i0])+a*np.linalg.norm(P[i0+1])
        print('   range',t,key,'stated',r,'model %.3f'%rr)
