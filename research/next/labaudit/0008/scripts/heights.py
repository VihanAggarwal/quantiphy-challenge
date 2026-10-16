import numpy as np
f=711.; cx=640.; cy=360.
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/normal.npy')
C=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/corners_captured_0008_10.npy')
def ray(p):
    r=np.array([p[0]-cx,p[1]-cy,f]); return r/np.linalg.norm(r)
def onplane(p,h):
    r=ray(p); t=-h/(n@r); return t*r
R=0.116
balls={'t1.0 f24':((531,157.5),1.401),'t1.2 f28.8':((574,382),1.564),'t1.5 f36':((548,304),1.5225)}
for h in [0.849,0.855,0.860]:
    print('--- camera height above desk plane h=%.3f'%h)
    P=[onplane(c,h) for c in C]
    cen=np.mean(P,0); 
    print(' table corner ranges',[round(np.linalg.norm(p),3) for p in P],'centre range %.3f'%np.linalg.norm(cen))
    for k,(px,rg) in balls.items():
        for mode,rr in [('surf->centre',rg+R),('as centre',rg)]:
            X=rr*ray(px); ht=n@X+h
            foot=X-(ht)*n   # vertical projection on table
            print(f'  {k} {mode}: centre height above desk {ht*100:.1f} cm; foot range {np.linalg.norm(foot):.3f}')
