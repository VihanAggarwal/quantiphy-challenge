import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
from geo import *
quad=np.load('book_quad.npy')  # TR, TL, BL, BR
def plane_pts(pts,down,f=F,pc=(666.4,617.9),rc=2.082):
    Pc=P(*pc,rc,f); d0=Pc@down
    out=[]
    for u,v in pts:
        r=ray(u,v,f); out.append(r*d0/(r@down))
    return np.array(out)
def dims(Q):
    e=[np.linalg.norm(Q[(i+1)%4]-Q[i]) for i in range(4)]
    # angle at corners
    angs=[]
    for i in range(4):
        a=Q[i-1]-Q[i]; b=Q[(i+1)%4]-Q[i]
        angs.append(np.degrees(np.arccos(a@b/np.linalg.norm(a)/np.linalg.norm(b))))
    return e,angs
for name,dn in [('roll',DOWN_ROLL),('noroll',DOWN_NOROLL)]:
    for f in (711,):
        Q=plane_pts(quad,dn,f)
        e,a=dims(Q)
        print(name,f,'edges cm',np.round(np.array(e)*100,1),'angles',np.round(a,1))
