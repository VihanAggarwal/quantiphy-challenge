import json, numpy as np
yh=540.4; cx=959.6
d=json.load(open('scripts/simulation_0143_t2.json'))
top=np.array([o['top'] for o in d],float); xt=np.array([o['xt'] for o in d]); low=np.array([o['low'] for o in d],float)
for f in [1867, 1890, 1920]:
    Hc = 1.8/1.40   # peak head height ratio (0141 & 0143 agree)
    K = f*Hc
    Zh = K*(1.40-1)/(yh-top)            # head-top depth, exact at bob peak
    X = (xt-cx)*Zh/f                     # torso lateral
    t = np.arange(len(d))/24
    # smoothing: centred moving average over one step (12 frames) then central/backward differences
    def ma(a,w=12):
        k=np.ones(w)/w; return np.convolve(a,k,mode='valid'), w
    Zs,w = ma(Zh); Xs,_ = ma(X); ts = t[w//2-1: w//2-1+len(Zs)] + 0.5/24
    v = np.hypot(np.gradient(Zs,ts), np.gradient(Xs,ts))
    out = {round(float(tt),3): round(float(vv),3) for tt,vv in zip(ts,v)}
    def at(T): return float(np.interp(T, ts, v))
    print('f',f,'K',round(K),'v(0.5)',round(at(0.5),2),'v(1)',round(at(1.0),2),'v(1.5)',round(at(1.5),2),'v(2)',round(at(2.0),2),'v(2.5)',round(at(2.5),2),'v(3)',round(at(3.0),2),'v(3.5)',round(at(3.5),2))
    # mean speed across whole-step windows between head-peaks
    pk=[0,12,25,37,49,62,75,87,98]
    for a,b in zip(pk[:-1],pk[1:]):
        dz=Zh[b]-Zh[a]; dx=X[b]-X[a]
        print('   peaks',a,b,'Z',round(Zh[a],2),'->',round(Zh[b],2),' v=',round(np.hypot(dz,dx)/((b-a)/24),2))
    # time-averaged path speeds using quadratic fit of the path length over 0.5..3.5s
