# v(hit) robustness: alternative frame conventions for the labeller's difference at the hit
import numpy as np, json
f=711.
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
def units(p):
    d=np.concatenate([(p-[640,360])/f,np.ones(p.shape[:-1]+(1,))],-1); return d/np.linalg.norm(d,axis=-1,keepdims=True)
THR=np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95])
def mra(a,L): return ((np.abs(a-L)/L)[...,None]<1-THR).mean(-1).mean()
rng=np.random.default_rng(2); N=40000
def mc(ka,kb,da,dmu,sz,known='a'):
    pa=uv[ka][None]+rng.normal(0,2,(N,2)); pb=uv[kb][None]+rng.normal(0,2,(N,2))
    db=da+rng.normal(dmu,0.004,N)+rng.normal(0,sz,N)
    return 25*100*np.linalg.norm(db[:,None]*units(pb)-da*units(pa),axis=1)
cases={'forward n31->32 (video 30->31), dR -1.2':(30,31,1.144,-0.012),
       'backward n30->31 (video 29->30), dR +2.6 (size)':(30,29,1.144,-0.026),
       'no 11/12 drop: n31=video31 -> video 32, dR -1.2':(31,32,1.144,-0.012),
       'hit frame = video 29 forward (29->30), dR +2.6':(29,30,1.144,+0.026)}
for nm,(ka,kb,da,dmu) in cases.items():
    for sz in [0.01,0.02,0.03]:
        L=mc(ka,kb,da,dmu,sz)
        grid=np.arange(20,200,1.); sc=[mra(a,L) for a in grid]
        print('%-50s sz %.0fcm  q5/50/95 %3.0f/%3.0f/%3.0f  opt %3.0f  E[score] cur100 %.2f  55 %.2f  60 %.2f'%(nm,100*sz,*np.percentile(L,[5,50,95]),grid[int(np.argmax(sc))],mra(100,L),mra(55,L),mra(60,L)))
