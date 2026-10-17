import json,numpy as np
f=711.0; cx,cy=640.0,360.0; D=0.040
W=json.load(open('wrad.json'))
ks=list(range(36,49)); cap=lambda k: k+2
rng=np.random.default_rng(0)
def run(variant,yh,anchorZ=1.3577,verbose=True):
    A=np.array([(cap(k),*W[str(k)][variant][:2]) for k in ks]); c,x,y=A.T; t=c/25
    # n_up for zero roll: horizon y=yh  -> n=(0,-1,(yh-cy)/f) normalized ... n.r = -(y-cy)/f + (yh-cy)/f
    n=np.array([0,-1,(yh-cy)/f]); n/=np.linalg.norm(n)
    r=np.c_[(x-cx)/f,(y-cy)/f,np.ones_like(x)]
    nr=r@n
    # anchor at capture 38 (video 36)
    hc=-anchorZ*nr[0]
    Z=-hc/nr; P=Z[:,None]*r
    i40=list(c).index(40); i41=list(c).index(41)
    raw=np.linalg.norm(P[i41]-P[i40])*2500
    res={'raw':raw,'hc':hc}
    for lo,hi,deg in [(38,50,1),(38,50,2),(38,44,1),(38,46,2),(39,43,1)]:
        m=(c>=lo)&(c<=hi)
        V=[np.polyval(np.polyder(np.polyfit(t[m],P[m,j],deg)),40.5/25) for j in range(3)]
        res['%d-%d d%d'%(lo,hi,deg)]=(np.linalg.norm(V)*100,*(np.array(V)*100))
    return res,Z,P,c
for variant in [0,1]:
    for yh in [355,358,359,360,361,362,364]:
        res,Z,P,c=run(variant,yh)
        print('v%d yh=%d hc=%.3f raw=%.1f '%(variant,yh,res['hc'],res['raw'])+' | '.join('%s %.1f(vx%.1f vz%.1f)'%(k,v[0],v[1],v[3]) for k,v in res.items() if k not in('raw','hc')))
res,Z,P,c=run(0,360.5)
print('Z',dict(zip(c.astype(int).tolist(),Z.round(4).tolist())))
print('X',dict(zip(c.astype(int).tolist(),P[:,0].round(4).tolist())))
