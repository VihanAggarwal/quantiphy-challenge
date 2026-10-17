import numpy as np
from bq import brentq
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
def proj(P): return np.array([f*P[0]/P[2]+cx, f*P[1]/P[2]+cy])
N=np.load('normals.npy')
def rim_width(C,u,R,n=720):
    # horizontal image extent of circle centre C, normal u, radius R
    a=np.cross(u,[0,0,1.]); a/=np.linalg.norm(a); b=np.cross(u,a)
    t=np.linspace(0,2*np.pi,n)
    pts=C[None,:]+R*(np.cos(t)[:,None]*a+np.sin(t)[:,None]*b)
    uv=np.array([proj(p) for p in pts])
    return uv[:,0].max()-uv[:,0].min(), uv
for rng_click,click_v in [(2.516,425),(2.516,430),(2.516,418)]:
  for ui,u in enumerate(list(N)+[np.array([0,-np.cos(np.radians(36)),-np.sin(np.radians(36))])]):
    r_=ray(565,click_v); P=rng_click*r_
    sin_th=-(r_@u); cos_th=np.sqrt(1-sin_th**2)
    rbody=0.0435
    Pax=P+rbody/cos_th*r_
    # find dh so rim centre projects to v=411
    g=lambda dh: proj(Pax+dh*u)[1]-411.
    dh=brentq(g,-0.3,0.3)
    C=Pax+dh*u
    Rs=brentq(lambda R: rim_width(C,u,R)[0]-26.3,0.01,0.1)
    print(f'click v={click_v} u#{ui} theta={np.degrees(np.arcsin(sin_th)):.1f} dh={dh*100:.1f}cm zC={C[2]:.3f} zclick={P[2]:.3f} rim diam={2*Rs*100:.2f}cm  (simple 26.3*zclick/f={26.3*P[2]/f*100:.2f})')
