import numpy as np
c=np.array([640.,360.])
FL=np.array([201.8,530.0]); FR=np.array([974.7,530.0]); BL=np.array([386.0,440.4]); BR=np.array([807.2,441.2])
def ray(p,f): return np.array([(p[0]-c[0])/f,(p[1]-c[1])/f,1.])
for f in [690,700,711,720,730]:
    r={k:ray(v,f) for k,v in dict(FL=FL,FR=FR,BL=BL,BR=BR).items()}
    # s_FL r_FL + s_BR r_BR - s_FR r_FR - s_BL r_BL = 0, fix s_FL=1
    A=np.stack([r['BR'],-r['FR'],-r['BL']],1); b=-r['FL']
    s=np.linalg.solve(A,b)
    P={'FL':r['FL'],'BR':s[0]*r['BR'],'FR':s[1]*r['FR'],'BL':s[2]*r['BL']}
    w=P['FR']-P['FL']; dd=P['BL']-P['FL']
    cosang=w@dd/np.linalg.norm(w)/np.linalg.norm(dd)
    ratio=np.linalg.norm(w)/np.linalg.norm(dd)
    print(f'f={f} cos={cosang:.4f} W/D={ratio:.4f} (76/60.3={76/60.3:.4f}, 60.3/76={60.3/76:.4f})')
