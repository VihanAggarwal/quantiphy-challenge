import numpy as np, json
from lsq import least_squares
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0054/m2_indep/'
T=json.load(open(OUT+'bx_track.json'))
cap=lambda i: int(np.floor(i*25/24+0.5))
f=711.; cx,cy=640.,360.
def proj(P): return np.c_[f*P[:,0]/P[:,2]+cx, f*P[:,1]/P[:,2]+cy]
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
anchor={'white':1.235,'green':1.331}; rad={'white':0.0335,'green':0.0335}
sel={'white':[i for i in range(22,38)], 'green':[i for i in range(22,32)]+[34,35]}
obs={}
for k in sel:
    o=[t for t in T if t['obj']==k and t['i'] in sel[k]]
    obs[k]=(np.array([cap(t['i']) for t in o]),np.array([[t['x'],t['y']] for t in o]))
def gdir(th,ph): return np.array([np.sin(th)*np.cos(ph),np.cos(th),np.sin(th)*np.sin(ph)])
def unpack(p): return p[0:6],p[6:12],gdir(p[12],p[13])
def traj(q,t,gd): return q[None,:3]+q[None,3:6]*t[:,None]+0.5*9.8*gd[None]*t[:,None]**2
def res(p,use_anchor=True):
    qw,qg,gd=unpack(p); rs=[]
    for q,k in ((qw,'white'),(qg,'green')):
        J,uv=obs[k]; t=(J-25)/25.
        rs.append((proj(traj(q,t,gd))-uv).ravel())
        if use_anchor: rs.append([(np.linalg.norm(q[:3])-anchor[k]-rad[k])*300])
    return np.concatenate(rs)
best=None
for th0 in (0.3,0.6,0.9,1.2):
    for ph0 in (-2.5,-1.5,-0.5,0.5,1.5,2.5):
        Pw=ray(377.6,248.9)*(anchor['white']+0.0335); Pg=ray(325.2,269.5)*(anchor['green']+0.0335)
        p0=np.r_[Pw,[1,-1,0],Pg,[1,-1,0],th0,ph0]
        s=least_squares(res,p0,iters=300)
        if best is None or s.cost<best.cost: best=s
s=best; qw,qg,gd=unpack(s.x)
print('rms px %.2f'%np.sqrt((s.fun[:-2]**2).mean()) if True else '', 'gravity dir in b cam',gd.round(3))
for q,k in ((qw,'white'),(qg,'green')):
    J,uv=obs[k]; t=(J-25)/25.; r=proj(traj(q,t,gd))-uv
    V=lambda j: q[3:6]+9.8*gd*(j-25)/25.
    Pc=lambda j: traj(q,np.array([(j-25)/25.]),gd)[0]
    print(k,'range c25 %.3f'%np.linalg.norm(q[:3]),'res rms %.2f'%np.sqrt((r**2).mean()),' |v| c37=%.2f c37.5=%.2f c38=%.2f c38.5=%.2f'%tuple(np.linalg.norm(V(j)) for j in (37,37.5,38,38.5)),' chord A c38-39=%.2f  B c37-38=%.2f'%(np.linalg.norm(Pc(39)-Pc(38))*25,np.linalg.norm(Pc(38)-Pc(37))*25), ' |v0|(c25)=%.2f'%np.linalg.norm(q[3:6]))
# free (no anchors) check
s2=least_squares(lambda p: res(p,False), s.x, iters=300)
qw2,qg2,gd2=unpack(s2.x)
print('free (gravity only): white range c25 %.3f green %.3f'%(np.linalg.norm(qw2[:3]),np.linalg.norm(qg2[:3])))
for q,k in ((qw2,'white'),(qg2,'green')):
    V=lambda j: q[3:6]+9.8*gd2*(j-25)/25.
    print('  ',k,'|v| c37.5=%.2f c38.5=%.2f'%(np.linalg.norm(V(37.5)),np.linalg.norm(V(38.5))))
