from common import *
from tracks import *
from fit_a import model, proj
# joint fit of both balls in one camera with free gravity direction (2 angles), |g|=9.81
def joint(trW,ksW,trG,ksG,g0):
    tsW=np.array([tcap(k) for k in ksW]); uvW=np.array([trW[k] for k in ksW])
    tsG=np.array([tcap(k) for k in ksG]); uvG=np.array([trG[k] for k in ksG])
    def gdir(a,b):
        d=np.array([np.sin(b)*np.cos(a),np.cos(b)*np.cos(a),np.sin(a)]); return d
    def res(p):
        g=gdir(p[12],p[13])
        r1=(proj(model(p[:6],tsW,1.0,g))-uvW).ravel(); r2=(proj(model(p[6:12],tsG,1.0,g))-uvG).ravel()
        return np.concatenate([r1,r2])
    a0=np.arcsin(g0[2]); b0=np.arctan2(g0[0],g0[1])
    p0=np.concatenate([ray(*trW[ksW[0]])*2,[-1,0,0],ray(*trG[ksG[0]])*2,[-1,0,0],[a0,b0]])
    s=least_squares(res,p0,iters=500)
    g=gdir(s.x[12],s.x[13])
    return s.x,g,np.sqrt(np.mean(s.fun**2))
db=np.load(OUT+'/b_down.npy')
for cam,trW,ksW,trG,ksG,g0 in [('a',A_W,list(range(24,38)),A_G_raw,list(range(24,37)),np.array([0,1.0,0])),('b',B_W,list(range(24,39)),B_G,list(range(24,37)),db)]:
    p,g,rms=joint(trW,ksW,trG,ksG,g0)
    print(cam,'free g dir',np.round(g,3),'pitch %.1f roll %.1f'%(np.degrees(np.arcsin(g[2])),np.degrees(np.arctan2(g[0],g[1]))),'rms %.2f'%rms)
    for nm,pp in [('W',p[:6]),('G',p[6:12])]:
        C=lambda t: model(pp,np.array([t]),1.0,g)[0]
        print('   %s r(1.0)=%.3f v(1.0)=%.2f fd25-26=%.2f fd37-38=%.2f fd38-39=%.2f v(1.6)=%.2f'%(nm,np.linalg.norm(C(1.0)),np.linalg.norm(pp[3:6]),np.linalg.norm(C(1.04)-C(1.0))*25,np.linalg.norm(C(1.52)-C(1.48))*25,np.linalg.norm(C(1.56)-C(1.52))*25,np.linalg.norm(pp[3:6]+9.81*g*0.6)))
