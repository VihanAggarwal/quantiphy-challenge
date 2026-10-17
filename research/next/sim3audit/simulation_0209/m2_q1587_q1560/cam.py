import numpy as np
CX,CY=1062.0,540.0
def ray(u,v,f):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def to_world(Pc,th):
    # world: X right, Yw forward(horizontal), Zw up ; camera pitched down by th
    X,Y,Z=Pc; c,s=np.cos(th),np.sin(th)
    return np.array([X, Z*c - Y*s, -(Y*c + Z*s)])
def pt_range(u,v,R,f,th): return to_world(ray(u,v,f)*R,th)
def on_plane(u,v,h,f,th):
    d=to_world(ray(u,v,f),th)   # world direction
    t=-h/d[2]; return d*t
def project(Pw,f,th):
    X,Yf,Zu=Pw; c,s=np.cos(th),np.sin(th)
    # invert to_world: Yf = Z c - Y s ; -Zu = Y c + Z s
    Zc = Yf*c - Zu*s ; Yc = -Zu*c - Yf*s
    return np.array([CX+f*X/Zc, CY+f*Yc/Zc])
