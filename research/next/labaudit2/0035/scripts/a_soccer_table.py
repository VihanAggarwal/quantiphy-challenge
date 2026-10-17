# per-frame soccer table in take a, late phase: pixel, x-mask diameter, plane range, size range scaled to the 1.6 s label
import labelstyle as L
from geom import *
xo={int(k):v for k,v in json.load(open(f'{OUT}/xmask_a_sb.json')).items()}
tr=load_tr('a')['sb']
for f in [711]:
    M=L.Model('a',f,1.5)
    d40=tr[38]; g40=1/((xo[38]['deq']-1)*cosa(d40['cx'],d40['cy'],f)**1.5); k=(3.052+0.089)/g40
    print('video cap   u      v    xdeq  plane_surf  size_surf(x, scaled@1.6)')
    for v in range(28,47):
        d=tr[v]; g=1/((xo[v]['deq']-1)*cosa(d['cx'],d['cy'],f)**1.5)
        rp=np.linalg.norm(plane_point(d['cx'],d['cy'],M.n,M.h,0.089,f))-0.089
        print(f'{v:4d} {cap(v):4d} {d["cx"]:6.1f} {d["cy"]:6.1f} {xo[v]["deq"]:5.1f}   {rp:.3f}      {k*g-0.089:.3f}')
    # linear fits of range vs capture time (cap 33..48)
    C=np.array([cap(v) for v in range(31,47)])
    rp=np.array([np.linalg.norm(plane_point(tr[v]['cx'],tr[v]['cy'],M.n,M.h,0.089,f))-0.089 for v in range(31,47)])
    rs=np.array([k/((xo[v]['deq']-1)*cosa(tr[v]['cx'],tr[v]['cy'],f)**1.5)-0.089 for v in range(31,47)])
    print('radial rate cap %d-%d: plane %.1f cm/s, size(x) %.1f cm/s'%(C[0],C[-1],100*np.polyfit(C*0.04,rp,1)[0],100*np.polyfit(C*0.04,rs,1)[0]))
    X=np.array([tr[v]['cx'] for v in range(31,47)]); Y=np.array([tr[v]['cy'] for v in range(31,47)])
    vx=np.polyfit(C,X,1)[0]; vy=np.polyfit(C,Y,1)[0]
    print('image speed %.2f px/frame -> lateral at 3.052 m: %.1f cm/s (f=711), %.1f (f=763)'%(np.hypot(vx,vy),100*3.052*np.hypot(vx,vy)/711*25,100*3.052*np.hypot(vx,vy)/763*25))
