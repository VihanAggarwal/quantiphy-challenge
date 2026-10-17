import numpy as np
f=711.; cy=360.; fps=25.; g=9.8
def fitZ(t,v,Vz,drag):
    best=None
    for Z0 in np.arange(1.8,4.5,0.002):
        s=(t-36)/fps; Z=Z0+Vz*s
        # v = cy + f*(Y0+Vy s + .5 g' s^2)/Z  -> linear in Y0,Vy
        A=np.c_[f/Z, f*s/Z]; b=v-cy-f*0.5*g*(1-drag)*s**2/Z
        c,*_=np.linalg.lstsq(A,b,rcond=None); r=A@c-b; e=np.sqrt(np.mean(r**2))
        if best is None or e<best[0]: best=(e,Z0)
    return best
t=np.array([33,34,35,37,38,39],float); v=np.array([324.3,351.6,381.9,451.3,490.4,535.3])
tb=np.array([33,34,35,37,38,39,40],float); vb=np.array([309.2,331.1,356.6,418.6,458.3,497.8,544.3])
print('BOX centroid')
for drag in [0,0.1,0.2,0.25]:
    for Vz in [0,-0.5,-1.0,0.5]:
        e,Z0=fitZ(t,v,Vz,drag); print('  drag %.2f Vz %+.1f  Z(c36)=%.3f Z(c40)=%.3f rms %.2f'%(drag,Vz,Z0,Z0+Vz*4/fps,e))
print('BOX centroid c34-39')
for drag in [0,0.1,0.2]:
    e,Z0=fitZ(t[1:],v[1:],0,drag); print('  drag %.2f Z=%.3f rms %.2f'%(drag,Z0,e))
print('BALL')
for drag in [0,0.05]:
    e,Z0=fitZ(tb,vb,0,drag); print('  drag %.2f Z=%.3f rms %.2f'%(drag,Z0,e))
    e,Z0=fitZ(tb[1:],vb[1:],0,drag); print('  c34+ drag %.2f Z=%.3f rms %.2f'%(drag,Z0,e))
    e,Z0=fitZ(tb[:-1],vb[:-1],0,drag); print('  c33-39 drag %.2f Z=%.3f rms %.2f'%(drag,Z0,e))
print('--- o-render tracks ---')
t=np.array([33,34,35,37,38,39],float)
for lab,v in [('box cy',np.array([324.9,350.9,380.8,457.7,490.4,528.8])),('box mid',np.array([327.0,352.0,380.5,456.5,490.0,529.0])),
              ('box top',np.array([295,319,349,421,456,496.])),('box bot',np.array([359,385,412,492,524,562.]))]:
    for sl in [slice(0,6),slice(1,6),slice(0,5)]:
        e,Z0=fitZ(t[sl],v[sl],0,0); print('  %s %s Z=%.3f rms %.2f'%(lab,sl,Z0,e))
tb=np.array([34,35,37,38,39,40],float)
for lab,v in [('ball cy',np.array([326.3,352.9,417.8,457.7,496.4,537.9])),('ball mid',np.array([325.5,351.0,417.5,458.0,496.5,540.0]))]:
    for sl in [slice(0,6),slice(0,5)]:
        e,Z0=fitZ(tb[sl],v[sl],0,0); print('  %s %s Z=%.3f rms %.2f'%(lab,sl,Z0,e))
