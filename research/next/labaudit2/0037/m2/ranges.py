import numpy as np, cv2
from cyl import pose, ray_plane
objs={'card':((563,540),None,0.679),'cup':((776,440),(776,504),0.845),'tape':((556,451),(556,472.5),1.038),'jar':((471,447),(471,485.5),1.008),'poker':((688,458),(688,497),0.905)}
for f in [680,711,740]:
    K,rv,tv,res=pose(f); R,_=cv2.Rodrigues(rv)
    out=[]
    for k,(c,b,d) in objs.items():
        if b is None:
            P,cam=ray_plane(K,rv,tv,c)
        else:
            Pb,cam=ray_plane(K,rv,tv,b)
            # vertical line through Pb: find z s.t. projection v matches c[1]
            dc=R.T@np.linalg.inv(K)@np.array([c[0],c[1],1.])
            # closest point on ray to vertical line x=Pb.x,y=Pb.y: solve in horizontal plane
            # param s along ray: cam + s*dc ; horizontal distance to Pb minimized
            hd=dc[:2]; s=((Pb[:2]-cam[:2])@hd)/(hd@hd)
            P=cam+s*dc
        rng=np.linalg.norm(P-cam)
        out.append(f'{k}: pred {rng:.3f} tof {d:.3f} ratio {d/rng:.3f}')
    print(f,' | '.join(out))
