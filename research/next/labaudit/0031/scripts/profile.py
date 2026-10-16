import numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit/0031/'
tr=json.load(open(D+'track.json'))
f=711.; cx,cy=640,360
Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1.]]))
pl=np.load(D+'scripts/plane_f711.npy'); n=pl[:3]; W=pl[3]; L=pl[4]
for r in ['0','x']:
  for key,Dm in [('W',4.0),('T',6.7)]:
    P=[]
    for i in range(49):
        t=tr[r][key][i]
        if t[1] is None: P.append(None); continue
        ray=Kinv@np.array([t[1],t[2],1.]); P.append((60.3/W-Dm/2)*ray/(n@ray))
    sp=[]
    for a in range(14,46,4):
        if P[a] is None or P[a+4] is None: continue
        sp.append('%d-%d:%.0f'%(a,a+4,np.linalg.norm(P[a+4]-P[a])/4*24))
    print(r,key,' '.join(sp))
