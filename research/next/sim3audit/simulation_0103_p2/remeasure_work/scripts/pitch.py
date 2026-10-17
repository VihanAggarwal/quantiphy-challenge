import numpy as np
def P(p,D,f,c=(480,480)):
    r=np.array([p[0]-c[0],p[1]-c[1],f],float); return D*r/np.linalg.norm(r)
def pitch_from(p1,p2,D1,D2,f,c=(480,480)):
    v=P(p2,D2,f,c)-P(p1,D1,f,c)
    return v, np.degrees(np.arctan2(-v[1],v[2])), np.linalg.norm(v)
for f in [3400,3460,3520]:
    print('f',f)
    print(' eagle', pitch_from((457.5,244.7),(865,255),100.1405,99.5206,f))
    for (bx,by) in [(610,590),(560,560),(640,600)]:
        print(' boat',(bx,by), pitch_from((bx,by),(bx-155.5,by-6.05),90.1103,90.4360,f))
