import numpy as np
cx,cy=960.,977.
def setup(f=2010., yh=1277., x0=1035., y0=1103., x24=1218., y24=1091.):
    p=np.arctan((yh-cy)/f)   # pitch up
    U=np.array([0,-np.cos(p),np.sin(p)])   # world up in cam coords (x right, y down, z fwd)
    H=np.array([0,np.sin(p),np.cos(p)])    # world horizontal forward
    X=np.array([1.,0,0])
    def P_of(u,v,R):
        r=np.array([(u-cx)/f,(v-cy)/f,1.]); return R*r/np.linalg.norm(r)
    P0=P_of(x0,y0,46.654); P24=P_of(x24,y24,43.970)
    d=P24-P0
    dh=np.array([d@X, d@H]); vert=d@U
    alpha=np.degrees(np.arctan2(-dh[1],dh[0]))
    return dict(f=f,p=p,U=U,H=H,X=X,P0=P0,P24=P24,d=d,alpha=alpha,vert=vert,speed=np.linalg.norm(d))
def point_on_line(G,u,v):
    # intersect pixel ray with 3D line P0 + s d (closest approach)
    f=G['f']; r=np.array([(u-cx)/f,(v-cy)/f,1.]); r/=np.linalg.norm(r)
    P0,d=G['P0'],G['d']
    # solve min |P0+s d - t r|
    A=np.stack([d,-r],1); s,t=np.linalg.lstsq(A,-P0,rcond=None)[0]
    return P0+s*d, s
def proj(G,P):
    return np.array([G['f']*P[0]/P[2]+cx, G['f']*P[1]/P[2]+cy])
def axes(G,alpha_deg):
    a=np.radians(alpha_deg)
    h=np.cos(a)*G['X']-np.sin(a)*G['H']      # heading (toward camera)
    l=np.sin(a)*G['X']+np.cos(a)*G['H']      # bird's left (far wing)
    return h,l,G['U']
def jac(G,P,vec):
    # image displacement per metre along vec at P
    e=1e-3; return (proj(G,P+e*vec)-proj(G,P-e*vec))/(2e-3)
if __name__=='__main__':
    for f in [1900,2010,2100]:
        for (x0,x24) in [(1035,1218),(1027,1218),(1043,1218),(1035,1213),(1035,1223)]:
            G=setup(f=f,x0=x0,x24=x24); print(f,x0,x24,'alpha',G['alpha'].round(1),'vert',G['vert'].round(2),'speed0-1',G['speed'].round(2))
