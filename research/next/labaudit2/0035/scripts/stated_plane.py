from geom import *
import itertools
def pts(take,f=F,Rs=0.089,swap=False):
    tr=load_tr(take)
    St={'a':[(15,'sb',2.758),(15,'bb',2.27),(40,'sb',3.052),(40,'bb',2.412)],
        'b':[(22.5,'sb',2.477),(22.5,'bb',2.7777),(35,'sb',2.373),(35,'bb',2.602)]}[take]
    if swap: St[2]=(35,'sb',2.602); St[3]=(35,'bb',2.373)
    out=[]
    for c,key,lab in St:
        if c==int(c): d=capframe_pos(tr[key],int(c))
        else:
            d1=capframe_pos(tr[key],int(c)); d2=capframe_pos(tr[key],int(c)+1); d={kk:(d1[kk]+d2[kk])/2 for kk in ['cx','cy','deq','minor']}
        R=0.116 if key=='bb' else Rs
        out.append((key,c,lab,R,d['cx'],d['cy'],(lab+R)*ray(d['cx'],d['cy'],f)))
    return out
for take,f,swap in [('a',711,False),('b',711,False),('b',711,True),('b',777,False)]:
    P=pts(take,f,swap=swap)
    print(f'== {take} f={f} swap={swap}')
    # plane through ball-centre points, soccer raised to bb-centre plane needs n: iterate
    n=np.array([0,-0.8,-0.6])
    for it in range(10):
        Q=np.array([p[6]+(0.116-p[3])*n for p in P]); n,hc=fit_plane(Q)
    res=Q@n+hc
    print('  4-pt plane n',np.round(n,3),'cam_h %.3f'%(hc+0.116),'pitch %.1f'%np.degrees(np.arcsin(-n[2])),'resid cm',np.round(100*res,1))
    for drop in range(4):
        Pk=[p for i,p in enumerate(P) if i!=drop]
        n=np.array([0,-0.8,-0.6])
        for it in range(10):
            Q=np.array([p[6]+(0.116-p[3])*n for p in Pk]); n,hc=fit_plane(Q)
        p=P[drop]; pred=np.linalg.norm(plane_point(p[4],p[5],n,hc+0.116,p[3],f))-p[3]
        print(f'  drop {p[0]}@{p[1]}: n={np.round(n,3)} cam_h={hc+0.116:.3f} pitch={np.degrees(np.arcsin(-n[2])):.1f}  predicted label {pred:.3f} vs {p[2]:.3f}')
