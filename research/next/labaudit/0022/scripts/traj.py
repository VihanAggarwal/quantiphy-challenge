import numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
C={k:np.array(v) for k,v in json.load(open(S+'corners.json')).items()}
T=json.load(open(S+'track_diff.json'))
CX,CY=640.,360.
FPS=24.0
def interp(tr,fi):
    i=int(np.floor(fi)); a=fi-i
    return (1-a)*np.array(tr[i][:2])+a*np.array(tr[i+1][:2])
for F in [711.0, 716.1]:
    pl=json.load(open(S+f'plane_{int(F)}.json')); n=np.array(pl['n'])
    def ray(p): return np.array([(p[0]-CX)/F,(p[1]-CY)/F,1.])
    def bp_range(p,R): r=ray(p); return R*r/np.linalg.norm(r)
    def onplane(p,d): r=ray(p); return d/np.dot(n,r)*r
    for rend in ['x','s']:
        tr=T[rend]
        stated={0.6:1.751,0.8:1.687,1.2:1.526}
        print(f'=== F={F} render {rend}')
        for tref,Rref in stated.items():
            pb=bp_range(interp(tr,tref*FPS),Rref)
            dball=n@pb; dt=dball-0.02
            P={k:onplane(C[k],dt) for k in ['FL','FR','NR','NL']}
            L=(np.linalg.norm(P['FR']-P['FL'])+np.linalg.norm(P['NR']-P['NL']))/2
            W=(np.linalg.norm(P['NL']-P['FL'])+np.linalg.norm(P['NR']-P['FR']))/2
            pred={t:np.linalg.norm(onplane(interp(tr,t*FPS),dball)) for t in stated}
            print(f' anchor t={tref}: table long {100*L:.1f} short {100*W:.1f}; predicted ranges',{t:round(v,3) for t,v in pred.items()})
