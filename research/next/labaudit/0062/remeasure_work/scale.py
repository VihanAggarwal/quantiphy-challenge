import numpy as np, json
cx=640.; cy=360.
for tag in ['711','free']:
    v=np.load('n_fit_%s.npy'%tag); n=v[:3]; L,W,f=v[3],v[4],v[5]
    C=json.load(open('board_corners_o.json'))
    def ray(u,v_): r=np.array([(u-cx)/f,(v_-cy)/f,1.]); return r
    print('==',tag,'f',round(f,1),'n',np.round(n,4))
    # board centre (diagonal intersection) per frame, range in units of h
    rng={}
    for k in ['31','33','34','36']:
        Q=np.array(C[k]); p=[np.r_[q,1] for q in Q]
        c=np.cross(np.cross(p[0],p[2]),np.cross(p[1],p[3])); c=c[:2]/c[2]
        r=ray(*c); X=r/(n@r); rng[int(k)]=np.linalg.norm(X)
        print(' board frame',k,'centre px',np.round(c,1),'range/h',round(rng[int(k)],4),'-> h from 2.815:',round(2.815/rng[int(k)],4))
    r336=rng[33]+0.6*(rng[34]-rng[33])
    print(' interp t=1.4 (frame 33.6): h=',round(2.815/r336,4), ' frame35 interp(34,36):', round(2.815/((rng[34]+rng[36])/2),4))
    # static objects: h = r * n.dhat  (point is at height e above floor -> h = r n.dhat + e)
    for name,(u,v_,r) in {'bag':(837.5,329.2,3.307),'box':(516.8,495.5,2.082),'mario':(635.1,623.8,2.016),'trash':(337.9,156.1,2.303)}.items():
        d=ray(u,v_); d/=np.linalg.norm(d)
        print(' ',name,'h(point)=',round(r*(n@d),4))
