# Monte Carlo of the label process for the motion rows: clicks with 2 px jitter, the stated ToF at the asked frame,
# the unknown next-frame ToF = stated + true radial change (route mixture) + ToF noise sigma_z.
# Reports label quantiles, the MRA-optimal answer and expected item scores of the current and candidate answers.
import numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.mra import item_scores
f=711.
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
def units(p):
    d=np.concatenate([(p-[640,360])/f,np.ones(p.shape[:-1]+(1,))],-1); return d/np.linalg.norm(d,axis=-1,keepdims=True)
THR=np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95])
def mra(a,L): return ((np.abs(a-L)/L)[...,None]<1-THR).mean(-1).mean()
rng=np.random.default_rng(1); N=40000
def speed_mc(k,d0,delta_mu,delta_sd,sz):
    p0=uv[k][None]+rng.normal(0,2,(N,2)); p1=uv[k+1][None]+rng.normal(0,2,(N,2))
    d1=d0+rng.normal(delta_mu,delta_sd,N)+rng.normal(0,sz,N)
    return 25*100*np.linalg.norm(d1[:,None]*units(p1)-d0*units(p0),axis=1)
def report(name,L,cands):
    grid=np.arange(20,260,1.0); sc=np.array([mra(a,L) for a in grid]); best=grid[np.argmax(sc)]
    q=np.percentile(L,[5,25,50,75,95])
    s=' '.join('%s=%.0f:%.3f'%(nm,a,mra(a,L)) for nm,a in cands.items())
    print('  %-34s q5/25/50/75/95 = %s  MRA-opt %.0f (%.3f) | %s'%(name,'/'.join('%.0f'%v for v in q),best,sc.max(),s))
    return best
rows={
 'v(1.0) video24->25':dict(k=24,d0=0.901,models={'route mix +4.7+-0.4':(0.047,0.004),'lin-interp +4.05':(0.0405,0.0),'plane A +4.8':(0.048,0.0),'size +5.5':(0.055,0.0)},
                       cands={'cur':99.456,'c125':125,'c130':130,'c137':137}),
 'v(hit) video30->31':dict(k=30,d0=1.144,models={'anchor/size -1.2+-0.3':(-0.012,0.003),'plane B -5.3 (rejected)':(-0.053,0.0),'plane A -6.6 (rejected)':(-0.066,0.0)},
                       cands={'cur':100.0,'c50':50,'c55':55,'c60':60}),
 'v(1.6) video38->39':dict(k=38,d0=1.027,models={'anchor/size -1.2+-0.3':(-0.012,0.003),'plane -0.6':(-0.006,0.0),'mix -0.9+-0.4':(-0.009,0.004)},
                       cands={'cur':47.31,'c45':45,'c50':50}),
}
for name,R in rows.items():
    print('==',name)
    for sz in [0.01,0.02,0.03]:
        print(' sigma_z = %.0f cm'%(100*sz))
        for mn,(mu,sd) in R['models'].items():
            L=speed_mc(R['k'],R['d0'],mu,sd,sz); report(mn,L,R['cands'])
