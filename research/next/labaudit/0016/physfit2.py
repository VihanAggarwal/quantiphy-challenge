import numpy as np,sys
sys.path.insert(0,'.'); from lm import least_squares
f=711.;cx,cy=640,360;g0=9.8
obs={32:(586.8,256.2),33:(640.8,198.8),34:(688.7,156.0),35:(735.2,121.1),36:(812.2,77.2),37:(844.7,70.3),38:(872.3,70.5),39:(894.5,77.3),40:(913.1,90.6)}
fr=sorted(obs); uv=np.array([obs[k] for k in fr])
def make(pitch=None,roll=None,gapfree=False,anchor=1.402):
    def unpack(p):
        P0=p[0:3];V=p[3:6];i=6
        th=np.radians(pitch) if pitch is not None else p[i]; i+= (pitch is None)
        ph=np.radians(roll) if roll is not None else p[i]; i+= (roll is None)
        gap=p[i] if gapfree else 1.0
        return P0,V,th,ph,gap
    def times(gap):
        return np.array([(k-36)/24 if k>=36 else (k-35-gap)/24 for k in fr])
    def pos(p,tt):
        P0,V,th,ph,gap=unpack(p)
        gd=np.array([np.sin(ph)*np.cos(th),np.cos(ph)*np.cos(th),np.sin(th)])
        return P0[None]+V[None]*tt[:,None]+0.5*g0*gd[None]*tt[:,None]**2
    def res(p):
        gap=unpack(p)[4]; P=pos(p,times(gap))
        u=cx+f*P[:,0]/P[:,2];v=cy+f*P[:,1]/P[:,2]
        return np.r_[u-uv[:,0],v-uv[:,1],(np.linalg.norm(pos(p,np.array([0.]))[0])-anchor)*500]
    return unpack,pos,res
def run(label,**kw):
    unpack,pos,res=make(**kw)
    n=6+(kw.get('pitch') is None)+(kw.get('roll') is None)+kw.get('gapfree',False)
    best=None
    for th0 in [0.3,0.7,1.0]:
      for vz in [-1,1,3]:
        p0=[0.3,-0.5,1.27,2,-1,vz]+([th0] if kw.get('pitch') is None else [])+([0.] if kw.get('roll') is None else [])+([1.5] if kw.get('gapfree') else [])
        r=least_squares(res,p0)
        if best is None or r.cost<best.cost: best=r
    p=best.x;rr=res(p);P0,V,th,ph,gap=unpack(p)
    P=pos(p,np.array([0,1/24]));fwd=np.linalg.norm(P[1]-P[0])*24
    print('%-28s rms %.2f px pitch %.1f roll %.1f gap %.2f |V36| %.2f fwd36-37 %.2f V36 %s'%(label,np.sqrt(np.mean(rr[:-1]**2)),np.degrees(th),np.degrees(ph),gap,np.linalg.norm(V),fwd,V.round(2)))
for pitch in [40,47,55]:
    run('uniform pitch%d roll0'%pitch,pitch=pitch,roll=0)
    run('gap free pitch%d roll0'%pitch,pitch=pitch,roll=0,gapfree=True)
run('gap free, g free',gapfree=True)
for gapv in [1.5,2.0]:
    pass
