import numpy as np, json
exec(open('fit3d.py').read().split("for name,imax in")[0])
r=rad['green']
for ua in (True,False):
    s,I,J,uv,P=fit('green',36,ua)
    Pc=lambda j: traj(s.x,np.array([(j-25)/25.]))[0]
    for c38uv in ((364.9,610.2),(363.8,610.6)):
        S38=ray(*c38uv)*(np.linalg.norm(Pc(38))-r)
        for c39uv in ((340.0,656.8),(341.7,654.1)):
            for H in (0.915,0.935):
                for delta in (0.0,0.02):
                    rr=ray(*c39uv); sc=(H-r-delta)/(rr@down)  # center on plane
                    C39=rr*sc; S39=rr*(np.linalg.norm(C39)-r)
                    v=np.linalg.norm(S39-S38)*25
                    print('anchor' if ua else 'free ', 'c38',c38uv,'c39',c39uv,'H',H,'delta',delta,'rng39=%.3f rng38=%.3f  A=%.3f m/s'%(np.linalg.norm(C39),np.linalg.norm(Pc(38)),v))
