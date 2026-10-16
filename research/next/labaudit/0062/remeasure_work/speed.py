import numpy as np, json
cx=640.; cy=360.
v=np.load('n_fit_711.npy'); n=v[:3]; f=v[5]
C=json.load(open('board_corners_o.json'))
P={}
for k,Q in C.items():
    k=int(k)
    if k<20: continue
    Q=np.array(Q); p=[np.r_[q,1] for q in Q]
    c=np.cross(np.cross(p[0],p[2]),np.cross(p[1],p[3])); c=c[:2]/c[2]
    r=np.array([(c[0]-cx)/f,(c[1]-cy)/f,1.]); P[k]=r/(n@r)
ks=sorted(P)
for a,b in zip(ks[:-1],ks[1:]):
    d=np.linalg.norm(P[b]-P[a])/(b-a)
    print(a,b,'disp/frame (h units)',round(d,4),' speed h/s @24fps',round(d*24,3),' implied h from 1.9339 m/s:',round(1.9339/(d*24),3), '@25fps', round(1.9339/(d*25),3))
# also mask centroid route from x render
