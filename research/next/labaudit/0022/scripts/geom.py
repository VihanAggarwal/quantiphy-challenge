import numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
C={k:np.array(v) for k,v in json.load(open(S+'corners.json')).items()}
CX,CY=640.,360.
def h(p): return np.array([p[0],p[1],1.])
def line(a,b): return np.cross(h(a),h(b))
def vp(l1,l2):
    p=np.cross(l1,l2); return p[:2]/p[2]
vA=vp(line(C['FL'],C['FR']),line(C['NL'],C['NR']))   # along far/near edges
vB=vp(line(C['FL'],C['NL']),line(C['FR'],C['NR']))   # along left/right edges
c=np.array([CX,CY])
f2=-np.dot(vA-c,vB-c)
print('vA',vA,'vB',vB,'f from orthogonality',np.sqrt(f2) if f2>0 else f2)
for F in [700,711,np.sqrt(f2)]:
    def ray(p): r=np.array([(p[0]-CX)/F,(p[1]-CY)/F,1.]); return r
    dA=ray(vA); dA/=np.linalg.norm(dA)
    dB=ray(vB); dB/=np.linalg.norm(dB)
    n=np.cross(dA,dB); n/=np.linalg.norm(n)
    # orient n toward camera (n . P <0 for points in front => choose n so that n.(-P)>0)
    # plane: n.X = d ; compute d from scale 1 by putting FL at depth along ray with arbitrary scale
    # aspect ratio from plane intersection with unit d
    d=1.0
    def onplane(p):
        r=ray(p); t=d/np.dot(n,r); return t*r
    P={k:onplane(C[k]) for k in ['FL','FR','NR','NL']}
    far=np.linalg.norm(P['FR']-P['FL']); near=np.linalg.norm(P['NR']-P['NL'])
    lef=np.linalg.norm(P['NL']-P['FL']); rig=np.linalg.norm(P['NR']-P['FR'])
    print(f'F={F:.1f} n={np.round(n,4)} angle(dA,dB)={np.degrees(np.arccos(abs(dA@dB))):.2f}  far/near/left/right (scale d=1):',np.round([far,near,lef,rig],4),
          'aspect long/short',round((far+near)/(lef+rig),4))
    json.dump({'F':F,'n':n.tolist()},open(S+f'plane_{int(F)}.json','w'))
