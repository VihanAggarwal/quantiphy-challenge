import numpy as np, json
exec(open('fit3d.py').read().split("for name,imax in")[0])
r=rad['green']
def run(ua,H,expo=0.8,verbose=False):
    s,I,J,uv,P=fit('green',36,ua)
    pre=lambda t: traj(s.x,np.atleast_1d(t))
    ts=np.linspace(13.0/25,14.5/25,30001)
    h=pre(ts)@down
    kb=np.argmax(h>=H-r); tb=ts[kb]; B=pre(tb)[0]
    # post-bounce: ballistic from B with unknown velocity; fit to video 38..41 (c40..c43)
    post=[x for x in obs['green'] if 38<=x[0]<=40]
    tj=np.array([(cap(x[0])-25)/25. for x in post]); uvp=np.array([[x[1],x[2]] for x in post])
    def res(v):
        PP=B[None]+v[None]*(tj-tb)[:,None]+0.5*9.8*down[None]*(tj-tb)[:,None]**2
        return (proj(PP)-uvp).ravel()
    sv=least_squares(res,np.array([-1.,-3.,-2.]))
    vpost=sv.x
    vpre=s.x[3:6]+9.8*down*tb
    def pos(t):
        t=np.atleast_1d(t)
        out=np.where((t<tb)[:,None], pre(t), B[None]+vpost[None]*(t-tb)[:,None]+0.5*9.8*down[None]*(t-tb)[:,None]**2)
        return out
    # simulate c39 exposure
    t39=(39-25)/25.; w=np.linspace(t39-expo/50,t39+expo/50,401)
    PP=pos(w); pr=proj(PP)
    cen=pr.mean(0); rng=np.linalg.norm(PP,axis=1).mean()
    # label: click at centroid, depth = mean range (surface)
    S39=ray(*cen)*(rng-r)
    t38=(38-25)/25.; w38=np.linspace(t38-expo/50,t38+expo/50,401); PP38=pos(w38); cen38=proj(PP38).mean(0); rng38=np.linalg.norm(PP38,axis=1).mean()
    S38=ray(*cen38)*(rng38-r)
    A=np.linalg.norm(S39-S38)*25
    # using observed clicks with simulated depth
    Aobs=np.linalg.norm(ray(340.0,656.8)*(rng-r)-ray(364.9,610.2)*(rng38-r))*25
    if verbose:
        print('  bounce c%.2f B=%s |vpre|=%.2f vpost=%s |vpost|=%.2f post-fit rms=%.2f px'%(25+tb*25,B.round(3),np.linalg.norm(vpre),vpost.round(2),np.linalg.norm(vpost),np.sqrt((sv.fun**2).mean())))
        print('  e_vert=%.2f'%(-(vpost@down)/(vpre@down)))
    return cen,rng,cen38,rng38,A,Aobs
for ua in (True,False):
    for H in (0.915,0.925,0.935):
        for expo in (0.6,0.8,1.0):
            cen,rng,cen38,rng38,A,Aobs=run(ua,H,expo,verbose=(expo==0.8))
            print('%s H=%.3f expo=%.1f: sim c38 centroid (%.1f,%.1f) rng %.3f | sim c39 centroid (%.1f,%.1f) rng %.3f | A_sim=%.3f  A_obsclicks=%.3f'%('anchor' if ua else 'free',H,expo,*cen38,rng38,*cen,rng,A,Aobs))
