# Which time base fits the free-flight image track (|g|=9.8, gravity dir free, no depth anchor)?
import numpy as np, sys
sys.path.insert(0,'.'); from lm import least_squares
f=711.; cx0,cy0=640.,360.
cent={33:(640.8,198.8),34:(688.7,156.0),35:(735.2,121.1),36:(812.2,77.2),37:(844.7,70.3),38:(872.3,70.5),39:(894.5,77.3),40:(913.1,90.6)}
def fitrms(times,frames):
    t=np.array(times); obs=np.array([cent[k] for k in frames])
    def res(p):
        th,ph=p[6],p[7]; g=9.8*np.array([np.cos(th)*np.sin(ph),np.cos(th)*np.cos(ph),np.sin(th)])
        X=p[None,0:3]+p[None,3:6]*t[:,None]+0.5*g[None]*t[:,None]**2
        return (np.c_[cx0+f*X[:,0]/X[:,2],cy0+f*X[:,1]/X[:,2]]-obs).ravel()
    best=None
    for th0 in np.radians([15,30,45,60]):
        for ph0 in np.radians([-30,-10,10]):
            for z in [1.0,1.4,1.8]:
                s=least_squares(res,np.r_[0.2,-0.4,z,1,-0.5,1,th0,ph0])
                if best is None or s.cost<best.cost: best=s
    p=best.x; th,ph=p[6],p[7]
    X=p[0:3]; return np.sqrt(np.mean(best.fun**2)),np.degrees(th),np.degrees(ph),np.linalg.norm(X)
frames=list(range(33,41))
for name,cap in [('25fps drop after 35',lambda k:k+(k>=36)),('25fps no drop',lambda k:k),('24fps',lambda k:k*25/24),
                 ('drop after 34',lambda k:k+(k>=35)),('drop after 36',lambda k:k+(k>=37)),('drop after 33',lambda k:k+(k>=34)),('drop after 37',lambda k:k+(k>=38))]:
    r=fitrms([cap(k)/25 for k in frames],frames)
    print('%-22s rms %.2f px  pitch %.1f roll %.1f  range@t0 %.2f'%(name,*r))
