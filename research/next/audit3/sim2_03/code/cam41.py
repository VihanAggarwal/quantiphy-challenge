import numpy as np

def brentq(fn,a,b,it=200):
    fa=fn(a)
    for _ in range(it):
        m=(a+b)/2; fm=fn(m)
        if (fm>0)==(fa>0): a,fa=m,fm
        else: b=m
    return (a+b)/2
f=5900.; al=np.radians(52.6); pp=np.array([540.,540.])
d=np.array([0,np.cos(al),-np.sin(al)]); u=np.array([0,np.sin(al),np.cos(al)]); r=np.array([1.,0,0])
def proj(P,Hc):
    Q=np.array(P)-np.array([0,0,Hc]); zc=Q@d
    return np.array([pp[0]+f*(Q@r)/zc, pp[1]-f*(Q@u)/zc])
def back(uv,Z,Hc):
    # ray from camera
    x=(uv[0]-pp[0])/f; y=-(uv[1]-pp[1])/f
    ray=d+x*r+y*u
    C=np.array([0,0,Hc]); t=(Z-Hc)/ray[2]
    return C+t*ray
# boat centroid track (0041 seg, frames 6 and 54)
c6=np.array([492.73,981.81]); c54=np.array([221.26,905.64])
def speed(Hc,z=1.5):
    p1=back(c6,z,Hc); p2=back(c54,z,Hc)
    return np.linalg.norm((p2-p1)[:2])/48*24
Hc=brentq(lambda h: speed(h)-4.0, 50, 400)
print('Hc for boat speed 4.0: %.1f m'%Hc)
for z in [0.5,1.5,2.5]:
    print(' z=%.1f -> speed %.3f'%(z,speed(Hc,z)))
# local scales at mast base
base=np.array([295.,885.]); top=np.array([288.,784.])
for zr in [3.0,3.7,4.5]:
    P=back(base,zr,Hc)
    m=brentq(lambda mm: proj(P+np.array([0,0,mm]),Hc)[1]-top[1], 0.1, 20)
    pt=proj(P+np.array([0,0,m]),Hc)
    print('roof z=%.1f: mast above roof %.3f m (top proj x %.1f); zc %.1f; horiz px/m %.2f'%(zr,m,pt[0],(P-np.array([0,0,Hc]))@d, f/((P-np.array([0,0,Hc]))@d)))
# person speed check, person centroid track frames 6..54 (height ~1.0 m centroid)
p6=np.array([359.22,395.53]); p54=np.array([363.71,466.79])
for z in [0.9,1.0]:
    a=back(p6,z,Hc); b=back(p54,z,Hc); print('person speed (centroid z=%.1f) %.3f m/s'%(z,np.linalg.norm((b-a)[:2])/48*24))

print('--- beam direction ---')
# heading on ground from centroid motion
a=back(c6,1.5,Hc); b=back(c54,1.5,Hc); h=(b-a)[:2]; h/=np.linalg.norm(h)
bdir=np.array([-h[1],h[0],0.])
print('heading (ground)',h,'beam dir',bdir[:2])
zs=2.3
for pt in [(250,940),(230,935),(270,945)]:
    P=back(np.array(pt,float),zs,Hc)
    for L in [1,2,3]:
        Q=P+bdir*L; print(pt,'beam +%dm ->'%L,proj(Q,Hc).round(1), ' -%dm ->'%L, proj(P-bdir*L,Hc).round(1))
    # heading direction in image
    print('   heading +1m ->',proj(P+np.r_[h,0],Hc).round(1),' base',proj(P,Hc).round(1))

print('--- beam at station via back-projection ---')
for zs in [1.5,2.3,3.0]:
    for near,far in [((215.1,941.8),(248.6,864.3)),((180,912.5),(214,863.5))]:
        A=back(np.array(near),zs,Hc); B=back(np.array(far),zs,Hc)
        dv=(B-A)[:2]
        print('zs=%.1f near %s far %s : |d|=%.3f perp=%.3f along=%.3f'%(zs,near,far,np.linalg.norm(dv),abs(dv@bdir[:2]),dv@h))
