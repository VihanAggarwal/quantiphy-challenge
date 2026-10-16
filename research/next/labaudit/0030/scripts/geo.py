import numpy as np, json
c=np.array([640.,360.]); f=711.
FL=np.array([201.8,530.0]); FR=np.array([974.7,530.0]); BL=np.array([386.0,440.4]); BR=np.array([807.2,441.2])
def ray(p): return np.array([(p[0]-c[0])/f,(p[1]-c[1])/f,1.])
r={k:ray(v) for k,v in dict(FL=FL,FR=FR,BL=BL,BR=BR).items()}
A=np.stack([r['BR'],-r['FR'],-r['BL']],1); s=np.linalg.solve(A,-r['FL'])
P={'FL':r['FL'],'BR':s[0]*r['BR'],'FR':s[1]*r['FR'],'BL':s[2]*r['BL']}
W=np.linalg.norm(P['FR']-P['FL']); D=np.linalg.norm(P['BL']-P['FL'])
def plane(scale):
    Q={k:v*scale for k,v in P.items()}
    n=np.cross(Q['FR']-Q['FL'],Q['BL']-Q['FL']); n/=np.linalg.norm(n)
    if n[1]>0: n=-n   # normal pointing up (camera y is down) 
    d=n@Q['FL']
    return Q,n,d
out={}
for name,scale in [('W76',0.76/W),('D603',0.603/D),('gm',np.sqrt(0.76/W*0.603/D))]:
    Q,n,d=plane(scale)
    print(name,'scale',scale,'n',n,'d(height of cam above table, m)',-d,'corner ranges',{k:round(float(np.linalg.norm(v)),3) for k,v in Q.items()})
    out[name]=dict(n=n.tolist(),d=float(d))
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit/0030/plane.json','w'))
