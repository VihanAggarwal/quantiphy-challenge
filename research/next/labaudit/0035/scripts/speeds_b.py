import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from recon import *
tr=load('bx'); bb=tr['bb']; sb=tr['sb']
# add soccer rest positions from earlier run (frames 0-9)
rest={0:(436.3,686.6,70.4),2:(437.3,685.7,68.2),4:(436.6,685.7,68.4),5:(436.5,685.7,68.2),7:(436.5,685.5,68.3),8:(436.5,685.7,68.4),9:(436.5,685.7,68.2)}
for k,(u,w,m) in rest.items(): sb[k]=dict(cx=u,cy=w,minor=m,major=m,A=np.pi*m*m/4)
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
T={k:orig(k)/25.0 for k in range(49)}
Ds=float(sys.argv[1]) if len(sys.argv)>1 else 0.181
def interp(P,t):
    x=t*24; i0=int(np.floor(x)); a=x-i0
    if i0 in P and i0+1 in P: return (1-a)*np.asarray(P[i0])+a*np.asarray(P[i0+1])
    return None
def pix(key,t):
    d=tr[key]; x=t*24; i0=int(np.floor(x)); a=x-i0
    return (1-a)*d[i0]['cx']+a*d[i0+1]['cx'],(1-a)*d[i0]['cy']+a*d[i0+1]['cy']
# stated points (assume 1.4s first=bb? test both)
St={'A':[(0.9,'sb',2.477),(0.9,'bb',2.7777),(1.4,'sb',2.602),(1.4,'bb',2.373)],
    'B':[(0.9,'sb',2.477),(0.9,'bb',2.7777),(1.4,'bb',2.602),(1.4,'sb',2.373)]}
Pb=size_track(bb,0.232); Ps=size_track(sb,Ds)
for nm,st in St.items():
    for t,key,r in st:
        P=Pb if key=='bb' else Ps
        print(nm,t,key,'stated',r,'size-model range %.3f'%np.linalg.norm(interp(P,t)))
planes={}
for nm,st in St.items():
    pts=[r*ray(*pix(key,t)) for t,key,r in st]
    n,c,s=fit_plane(pts); planes['stated4'+nm]=(n,c); print('plane',nm,np.round(n,3),'h',round(float(n@c),3),'sing',np.round(s,3))
n=np.array([0,-0.84,-0.54])
for it in range(10):
    p2=[Pb[i] for i in bb]+[Ps[i]+(0.116-Ds/2)*n for i in sb]
    n,c,s=fit_plane(p2)
planes['joint']=(n,c); print('joint',np.round(n,3),'h',round(float(n@c),3),'sing',np.round(s,3))
res=np.array([n@(p-c) for p in p2]); print('joint rms cm',100*np.sqrt((res**2).mean()))
def vfit(P,k,h=2):
    ks=[j for j in range(k-h,k+h+1) if j in P]
    t=np.array([T[j] for j in ks]); X=np.array([P[j] for j in ks])
    return np.linalg.norm(np.polyfit(t,X,1)[0])
def vfwd(P,k): return np.linalg.norm(P[k+1]-P[k])/(T[k+1]-T[k])
for name in ['size','stated4A','stated4B','joint']:
    if name=='size': B,Sc=Pb,Ps
    else:
        n,c=planes[name]; off=-(0.116-Ds/2) if name=='joint' else 0.0
        B=plane_track(bb,n,c,0.0); Sc=plane_track(sb,n,c,off)
    print(name)
    for t in [0.9,1.3,1.4]:
        k=int(round(t*24))
        print('  t=%.1f k%d  sb fwd %.0f fit %.0f | bb fwd %.0f fit %.0f'%(t,k,100*vfwd(Sc,k),100*vfit(Sc,k),100*vfwd(B,k),100*vfit(B,k)))
    for (k0,k1) in [(9,22),(10,22),(9,21)]:
        if k0 in Sc and k1 in Sc:
            print('  disp k%d-%d sb %.1f bb %.1f'%(k0,k1,100*np.linalg.norm(Sc[k1]-Sc[k0]),100*np.linalg.norm(B[k1]-B[k0])))
        else:
            print('  disp k%d-%d bb %.1f'%(k0,k1,100*np.linalg.norm(B[k1]-B[k0])))
