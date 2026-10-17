import numpy as np
from geom import *
sm=np.load('smooth.npy')
tips={ # frame: (near(u,v), far(u,v))
 24:((1160,1083),(1287,1111)),
 25:((1168,1087),(1310,1122)),
 26:((1188,1095),(1319,1128)),
 41:((1417,1067),(1559,1098)),
 42:((1433,1070),(1578,1108)),
 43:((1449,1078),(1591,1112)),
 23:((1160,1085),(1267,1097)),
}
for f in [1900,2010,2100]:
  G=setup(f=f)
  for da in [-4,0,4]:
    a=G['alpha']+da
    h,l,U=axes(G,a)
    out=[]
    for fr,(n,fa) in sorted(tips.items()):
        P,s=point_on_line(G,sm[0,fr],sm[1,fr])
        jl=jac(G,P,l); jU=jac(G,P,U); jh=jac(G,P,h)
        D=np.array(fa)-np.array(n)
        # solve D = S*(cos e * jl) + S*sin(phi)*jU (roll)  -> 2 unknowns A=S cos(e)cos(phi), B=S sin(phi)
        M=np.stack([jl,jU],1); A,B=np.linalg.solve(M,D)
        out.append((fr,round(P[2],2),jl.round(1),round(A,2),round(np.degrees(np.arcsin(np.clip(B/A,-1,1))),1), round(np.linalg.norm(D)/np.linalg.norm(jl),2)))
    print(f'f={f} alpha={a:.1f}')
    for o in out: print('   fr',o[0],'Z',o[1],'jl',o[2],'S(roll-solved)',o[3],'roll',o[4],'S(|D|/|jl|)',o[5])
