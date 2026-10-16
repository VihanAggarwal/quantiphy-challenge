# Sensitivity of the t=1.0 s ball-to-desk distance (label emulation) and the physical heights to f, ball click, desk click.
import numpy as np
C=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/corners_captured_0008_10.npy')
cx,cy=640.,360.; R=0.116
def setup(f):
    def ray(p):
        r=np.array([p[0]-cx,p[1]-cy,f]); return r/np.linalg.norm(r)
    BL,BR,FR,FL=C
    L=lambda a,b: np.cross([*a,1],[*b,1])
    v1=np.cross(L(FL,BL),L(FR,BR)); v2=np.cross(L(BL,BR),L(FL,FR))
    d1=np.array([v1[0]-cx*v1[2],v1[1]-cy*v1[2],f*v1[2]]); d2=np.array([v2[0]-cx*v2[2],v2[1]-cy*v2[2],f*v2[2]])
    n=np.cross(d1,d2); n/=np.linalg.norm(n); n=-n if n[1]>0 else n
    P=[(-1/(n@ray(c)))*ray(c) for c in C]
    side=np.linalg.norm(P[1]-P[2])+np.linalg.norm(P[3]-P[0]); width=np.linalg.norm(P[0]-P[1])+np.linalg.norm(P[2]-P[3])
    h=0.5*(0.76/(side/2)+0.603/(width/2))
    return ray,n,h,(side/2)/(width/2)
for f in [700.,711.,722.]:
    ray,n,h,asp=setup(f)
    out=[]
    for bp in [(532,157),(530,152),(534,162)]:
        Bs=1.401*ray(bp); Bc=1.517*ray(bp)
        hc=n@Bc+h
        # desk locus
        ds=[]
        for u in np.arange(560,641,5.):
            vs=np.arange(400,520,0.25); rr=np.array([-h/(n@ray((u,v))) for v in vs]); k=np.argmin(abs(rr-1.725))
            D=1.725*ray((u,vs[k])); ds.append(np.linalg.norm(Bs-D))
        out.append((bp,hc,min(ds),np.median(ds),max(ds)))
    print(f'f={f:.0f}: h={h:.3f} aspect(depth/width)={asp:.3f} (76/60.3={0.76/0.603:.3f})')
    for bp,hc,a,b,c in out: print(f'   ball click {bp}: physical centre height {100*hc:.1f}; emulation (as-is ball, desk on 1.725 locus u 560-640) min {100*a:.1f} med {100*b:.1f} max {100*c:.1f}')
