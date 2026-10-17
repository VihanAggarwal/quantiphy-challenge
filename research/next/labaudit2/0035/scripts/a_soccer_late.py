# Soccer in take a at 1.5 s and 1.6 s: variants of the plane and size routes
import labelstyle as L
from geom import *
from stated_plane import pts as stated_pts
xo={int(k):v for k,v in json.load(open(f'{OUT}/xmask_a_sb.json')).items()}
def plane_from(take,f,drop=None):
    P=stated_pts(take,f)
    P=[p for i,p in enumerate(P) if i!=drop]
    n=np.array([0,-0.8,-0.6])
    for it in range(10):
        Q=np.array([p[6]+(0.116-p[3])*n for p in P]); n,hc=fit_plane(Q)
    return n,hc+0.116
def run(f,plane_drop=None,mask='3way',delta=1.5,wsize=7,wpos=4):
    M=L.Model('a',f,delta)
    if plane_drop is not None: M.n,M.h=plane_from('a',f,plane_drop)
    if mask=='x':
        # replace size series with x-only deq (minus 1 px halo correction applied via delta)
        orig=L.series
        def series_x(take,key,dl):
            C,X,Y,D=orig(take,key,0.0)
            if key=='sb':
                D=np.array([xo[k]['deq'] if (k in xo and abs(xo[k]['deq']-dd)<6) else dd+3 for k,dd in zip([kk for kk in sorted(load_tr(take)[key])],D)])+dl
            return C,X,Y,D
        L.series=series_x
    old=L.smooth_at
    def sm(take,key,c,dl,wpos_=wpos,wsize_=wsize): return old(take,key,c,dl,wpos_,wsize_)
    L.smooth_at=sm
    out=[]
    for t in [1.5,1.6]:
        vs=[M.fwd_speed('sb',t,r)[0]*100 for r in 'SP']; lr=[M.lat_rad('sb',t,r) for r in 'SP']
        out.append(f't={t}: S {vs[0]:.1f} (lat {100*lr[0][0]:.0f} rad {100*lr[0][1]:+.0f}) P {vs[1]:.1f} (rad {100*lr[1][1]:+.0f})')
    L.smooth_at=old
    if mask=='x': L.series=orig
    return ' | '.join(out)
for f in [711,763]:
    for pd in [None,0]:
        for mask,delta in [('3way',0.0),('3way',1.5),('3way',3.0),('x',-1.0),('x',0.0)]:
            for ws in [5,7,10]:
                print(f'f={f} plane={"4pt" if pd is None else "3pt(no sb@0.6)"} mask={mask}{delta:+.1f} wsize={ws}: ',run(f,pd,mask,delta,ws))
