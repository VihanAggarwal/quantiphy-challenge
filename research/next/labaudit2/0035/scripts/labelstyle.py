# Label-style emulation for family 0035 motion rows.
# Clicked centre per capture frame (smoothed track), back-projected with a range from (S) apparent size or (P) the floor plane
# through the stated points, each scaled to the stated depth at the nearest stated time; forward difference on the 25 fps clock.
import sys
from geom import *
from stated_plane import pts as stated_pts
DT=0.04
PH={  # (take,ball): list of phases as capture-frame ranges [lo,hi] (inclusive) with no impulse inside
 ('a','sb'):[(10,20),(21,50)], ('a','bb'):[(0,7),(9,20),(21,50)],
 ('b','sb'):[(0,10),(15,26),(27,50)], ('b','bb'):[(0,11),(13,25),(28,50)]}
STATED={'a':{'sb':[(15,2.758),(40,3.052)],'bb':[(15,2.27),(40,2.412)]},
        'b':{'sb':[(22.5,2.477),(35,2.373)],'bb':[(22.5,2.7777),(35,2.602)]}}
def series(take,key,delta):
    tr=load_tr(take)[key]
    C=[];X=[];Y=[];D=[]
    for k,d in sorted(tr.items()):
        C.append(cap(k)); X.append(d['cx']); Y.append(d['cy']); D.append(d['deq']+delta)
    return np.array(C,float),np.array(X),np.array(Y),np.array(D)
def phase_of(take,key,c):
    for lo,hi in PH[(take,key)]:
        if lo<=c<=hi: return lo,hi
    return None
def smooth_at(take,key,c,delta,wpos=4,wsize=7):
    C,X,Y,D=series(take,key,delta)
    lo,hi=phase_of(take,key,c)
    m=(C>=max(lo,c-wpos))&(C<=min(hi,c+wpos))
    if m.sum()<4: m=(C>=lo)&(C<=min(hi,lo+2*wpos))
    deg=2 if m.sum()>=5 else 1
    px=np.polyval(np.polyfit(C[m]-c,X[m],deg),0); py=np.polyval(np.polyfit(C[m]-c,Y[m],deg),0)
    m2=(C>=max(lo,c-wsize))&(C<=min(hi,c+wsize))
    # range ~ 1/(d cos^1.5): fit 1/(d*cos^1.5) linearly
    return px,py,C[m2],X[m2],Y[m2],D[m2]
class Model:
    def __init__(s,take,f,delta=1.5,Rs=0.089):
        s.take=take; s.f=f; s.delta=delta; s.R={'bb':0.116,'sb':Rs}
        P=stated_pts(take,f,Rs=Rs)
        n=np.array([0,-0.8,-0.6])
        for it in range(10):
            Q=np.array([p[6]+(0.116-p[3])*n for p in P]); n,hc=fit_plane(Q)
        s.n=n; s.h=hc+0.116
    def pix(s,key,c): return smooth_at(s.take,key,c,s.delta)[:2]
    def size_inv(s,key,c):
        px,py,C,X,Y,D=smooth_at(s.take,key,c,s.delta)
        g=1.0/(D*cosa(X,Y,s.f)**1.5)       # proportional to centre range
        return np.polyval(np.polyfit(C-c,g,1),0)
    def raw_range(s,key,c,route):
        u,v=s.pix(key,c); R=s.R[key]
        if route=='P': return np.linalg.norm(plane_point(u,v,s.n,s.h,R,s.f))-R
        return s.size_inv(key,c)   # unscaled
    def scale(s,key,route,c):
        # scale so the model matches the stated depth at the nearest stated time
        st=STATED[s.take][key]; cs,lab=min(st,key=lambda x:abs(x[0]-c))
        if route=='P': return lab/s.raw_range(key,cs,'P'),0.0
        # size: centre range = k*g ; surface = k*g - R  -> k=(lab+R)/g
        return (lab+s.R[key])/s.size_inv(key,cs),s.R[key]
    def label_point(s,key,c,route,cref):
        k,R=s.scale(key,route,cref)
        u,v=s.pix(key,c)
        rng=k*s.raw_range(key,c,route)-R if route=='S' else k*s.raw_range(key,c,route)
        return rng*ray(u,v,s.f)
    def fwd_speed(s,key,t,route):
        n=t*25; out=[]
        for c0 in sorted(set([np.floor(n),np.ceil(n)])):
            P0=s.label_point(key,c0,route,n); P1=s.label_point(key,c0+1,route,n)
            out.append(np.linalg.norm(P1-P0)/DT)
        return np.mean(out),out
    def lat_rad(s,key,t,route):
        n=t*25; c0=np.floor(n)
        P0=s.label_point(key,c0,route,n); P1=s.label_point(key,c0+1,route,n)
        d=P1-P0; u=P0/np.linalg.norm(P0); rad=d@u; lat=np.linalg.norm(d-rad*u)
        return lat/DT,rad/DT
    def disp(s,key,t1,t2,route):
        out=[]
        for c1 in sorted(set([np.floor(t1*25),np.ceil(t1*25)])):
            for c2 in sorted(set([np.floor(t2*25),np.ceil(t2*25)])):
                out.append(np.linalg.norm(s.label_point(key,c2,route,t2*25)-s.label_point(key,c1,route,t1*25)))
        return np.mean(out),out
    def phys_speed(s,key,t,route='P'):
        # centre velocity from the smoothed track (central difference +-0.5 frame) on the plane, no label scaling
        n=t*25; R=s.R[key]
        def cen(c):
            u,v=s.pix(key,c)
            if route=='P': return plane_point(u,v,s.n,s.h,R,s.f)
            k,_=s.scale(key,'S',n); return k*s.size_inv(key,c)*ray(u,v,s.f)
        return np.linalg.norm(cen(n+0.5)-cen(n-0.5))/DT
if __name__=='__main__':
    ROWS={'a':[('sb','v',0.6,168),('bb','v',0.6,137),('sb','d',(0.5,0.6),16.6),('bb','d',(0.5,0.6),14.0),
               ('sb','v',1.5,54),('bb','v',1.5,46),('sb','v',1.6,44),('bb','v',1.6,36)],
          'b':[('sb','v',0.9,98),('bb','v',0.9,119),('sb','v',1.4,55),('bb','v',1.4,133),('sb','d',(0.4,0.9),86),
               ('bb','d',(0.4,0.9),91.65),('sb','v',1.3,50),('bb','v',1.3,122)]}
    for take in sys.argv[1:]:
        for f in [711,763]:
            for delta in [0.0,1.5,3.0]:
                M=Model(take,f,delta)
                print(f'== take {take} f={f} mask+{delta}px  plane n={np.round(M.n,3)} h={M.h:.3f} pitch={np.degrees(np.arcsin(-M.n[2])):.1f}')
                for key,kind,t,cur in ROWS[take]:
                    if kind=='v':
                        vs=[M.fwd_speed(key,t,r)[0]*100 for r in 'SP']
                        lr=[M.lat_rad(key,t,r) for r in 'SP']
                        ph=[M.phys_speed(key,t,r)*100 for r in 'SP']
                        print(f'  {key} v@{t}: label-style S {vs[0]:6.1f} P {vs[1]:6.1f} | lat/rad S {100*lr[0][0]:.0f}/{100*lr[0][1]:+.0f} P {100*lr[1][0]:.0f}/{100*lr[1][1]:+.0f} | phys S {ph[0]:.0f} P {ph[1]:.0f} | current {cur}')
                    else:
                        if key=='bb' and take=='b' and t[0]==0.4: 
                            print('  (bb disp b uses rest position: separate script)'); continue
                        ds=[M.disp(key,t[0],t[1],r)[0]*100 for r in 'SP']
                        print(f'  {key} disp {t}: S {ds[0]:.1f} P {ds[1]:.1f} | current {cur}')
