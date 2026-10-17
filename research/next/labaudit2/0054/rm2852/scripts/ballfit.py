import json, math, numpy as np
import sys; sys.path.insert(0, __import__("os").path.dirname(__file__)); from lm import least_squares
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
comps=json.load(open(S+'comps_ax.json'))
F=711.0; CX=640.0; CY=360.0
def cap(k): return math.floor(k*25/24+0.5)
def track(kind):
    out={}
    for k in range(22,42):
        for c in comps[str(k)]:
            b=c['bgr'][0]
            if c['area']>1500 or c['c'][1]>690: continue
            if (kind=='white' and b>=85) or (kind=='tennis' and b<85): out[cap(k)]=np.array(c['c'])
    return out
def ray(u,v):
    d=np.array([(u-CX)/F,(v-CY)/F,1.0]); return d/np.linalg.norm(d)
def gvec(th,rho,gm=9.81):
    return gm*np.array([-math.sin(rho), math.cos(rho)*math.cos(th), math.cos(rho)*math.sin(th)])
def model(p,ts,th,rho,gm):
    A=p[0:3]; V=p[3:6]
    G=gvec(th,rho,gm)
    tt=(ts-1.0)[:,None]
    return A+V*tt+0.5*G*tt**2
def proj(P): return np.c_[CX+F*P[:,0]/P[:,2], CY+F*P[:,1]/P[:,2]]
def fit(kind,c0,c1,anchor=None,free_g=False,th=None,rho=None,gm=9.81,sig_anchor=0.03):
    tr=track(kind); cs=np.array(sorted(c for c in tr if c0<=c<=c1)); uv=np.array([tr[c] for c in cs]); ts=cs/25.0
    def unpack(p):
        q=list(p[:6]); i=6
        t_=th; r_=rho; g_=gm
        if th is None: t_=p[i]; i+=1
        if rho is None: r_=p[i]; i+=1
        if free_g: g_=p[i]; i+=1
        return np.array(q),t_,r_,g_
    def res(p):
        q,t_,r_,g_=unpack(p)
        P=model(q,ts,t_,r_,g_)
        r=(proj(P)-uv).ravel()/1.5
        if anchor is not None:
            r=np.r_[r,(np.linalg.norm(q[:3])-anchor)/sig_anchor]
        return r
    u0,v0=tr[25] if 25 in tr else uv[0]
    A0=ray(u0,v0)*(anchor if anchor else 3.0)
    p0=list(A0)+[-1,-1,-1]
    if th is None: p0.append(0.03)
    if rho is None: p0.append(0.0)
    if free_g: p0.append(9.81)
    sol=least_squares(res,np.array(p0,float))
    q,t_,r_,g_=unpack(sol.x)
    P=model(q,ts,t_,r_,g_)
    rr=proj(P)-uv
    # covariance
    J=sol.jac; dof=max(1,len(sol.fun)-len(sol.x)); s2=(sol.fun**2).sum()/dof
    try: cov=np.linalg.inv(J.T@J)*s2
    except: cov=None
    return dict(q=q,th=t_,rho=r_,g=g_,rms=np.sqrt((rr**2).mean()),cs=cs,uv=uv,P=P,cov=cov,x=sol.x,res=rr)
def fd(fr,c):
    P=model(fr['q'],np.array([c/25,(c+1)/25]),fr['th'],fr['rho'],fr['g'])
    return np.linalg.norm(P[1]-P[0])*25
if __name__=='__main__':
    for kind,anc in [('white',3.0735+0.033),('tennis',3.039+0.0335)]:
        print('=====',kind)
        for c0,c1 in [(24,39),(25,39),(26,39),(24,38),(27,39)]:
            for lab,kw in [('free all',dict()),('anchored',dict(anchor=anc)),('anchored th=2.5deg rho=-0.6',dict(anchor=anc,th=math.radians(2.5),rho=math.radians(-0.6))),('anch th=1deg rho=0',dict(anchor=anc,th=math.radians(1),rho=0.0)),('anch free g',dict(anchor=anc,free_g=True))]:
                try:
                    r=fit(kind,c0,c1,**kw)
                except Exception as e:
                    print(lab,'ERR',e); continue
                rng25=np.linalg.norm(model(r['q'],np.array([1.0]),r['th'],r['rho'],r['g'])[0])
                print('%d-%d %-28s range@1.0=%.3f th=%.2fdeg rho=%.2fdeg g=%.2f rms=%.2fpx v37-38=%.3f v38-39=%.3f v36-37=%.3f |V(1.5)|=%.3f'%(c0,c1,lab,rng25,math.degrees(r['th']),math.degrees(r['rho']),r['g'],r['rms'],fd(r,37),fd(r,38),fd(r,36),np.linalg.norm(r['q'][3:6]+gvec(r['th'],r['rho'],r['g'])*0.5)))
