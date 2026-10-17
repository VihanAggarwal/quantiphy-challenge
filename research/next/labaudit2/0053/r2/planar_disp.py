import numpy as np, json, sys
sys.argv=[sys.argv[0],'34']
exec(open('planar.py').read().split('results=[]')[0])
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
P10=2.73*ray(T[10]['cx'],T[10]['cy']); r34=ray(T[34]['cx'],T[34]['cy'])
for pitch,roll in [(30,15),(32,14),(34,13),(35,11),(37,10),(34.7,10.1),(38.4,10.9),(37.4,1.4),(36,7),(37,8)]:
    n=nvec(pitch,roll)
    c,psi,phi=fitpair(n,34)
    e1,e2=basis(n); d=np.cos(phi)*e1+np.sin(phi)*e2
    R=rot(n,psi)
    A=np.c_[d,-r34]; sol=np.linalg.lstsq(A,-R@P10,rcond=None)[0]; lam,s=sol
    if lam<0:
        d=-d; sol=np.linalg.lstsq(np.c_[d,-r34],-R@P10,rcond=None)[0]; lam,s=sol
    P34=s*r34; miss=np.linalg.norm(R@P10+lam*d-P34)
    splane=(n@P10)/(n@r34)
    print(f'pitch {pitch:5.1f} roll {roll:5.1f} resid {c/len(data[34][0]):.3f} yaw {np.degrees(psi):6.2f} | planar-motion range34 {s:.3f} disp {np.linalg.norm(P34-P10):.3f} miss {miss*100:.1f}cm | const-height plane range34 {splane:.3f} disp {np.linalg.norm(splane*r34-P10):.3f}')
