import cv2, numpy as np, json
exec(open('/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/pnp2.py').read().split("for f in [711,750,780,800]")[0])
D='/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/'
tm={r[0]:r for r in json.load(open(D+'tm_x_24.json'))}
YOFF=5.4
def px(k):
    k0=int(np.floor(k)); a=k-k0
    if a==0: return np.array([tm[k0][1],tm[k0][2]+YOFF])
    return (1-a)*px(k0)+a*px(k0+1)
def ray(K,p):
    u=np.linalg.solve(K,[p[0],p[1],1.]); return u/np.linalg.norm(u)
for f in [700,711,730]:
    K,R,t,err=solve(f); Cw=-R.T@t; up=np.sign(Cw[2])
    def centre(k): return table_pt(K,R,t,px(k),h=2.0*up)
    print('f=%d'%f)
    for k0 in [21,21.5,22]:
        k1=34
        u0,u1=ray(K,px(k0)),ray(K,px(k1))
        c0,c1=centre(k0),centre(k1)
        # A: anchored label-style: r1=71.6 given, r0 = 71.6 + plane delta of surface ranges
        r1=71.6; r0=71.6+(np.linalg.norm(c0)-np.linalg.norm(c1))
        dA=np.linalg.norm(r1*u1-r0*u0)
        # A2: both at 71.6 (no depth change)
        dA2=np.linalg.norm(71.6*(u1-u0))
        # B: plane-only surface points (unanchored)
        s0=(np.linalg.norm(c0)-2)*u0; s1=(np.linalg.norm(c1)-2)*u1
        dB=np.linalg.norm(s1-s0)
        # C: physical centre displacement from plane (unanchored)
        dC=np.linalg.norm(c1-c0)
        # D: physical centre, scaled so that surface range at 34 = 71.6
        sc=(71.6+2)/np.linalg.norm(c1); dD=dC*sc
        print('  %4.1f->34 dpx=%.1f  A(anchored label)=%.2f  A2(const r)=%.2f  B(plane surf)=%.2f  C(phys centre plane)=%.2f  D(phys centre anchored)=%.2f'%(k0,np.linalg.norm(px(k1)-px(k0)),dA,dA2,dB,dC,dD))
