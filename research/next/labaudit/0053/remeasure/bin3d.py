import numpy as np
f=711.0; cx=640.0; cy=360.0
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.0]); return d/np.linalg.norm(d)
T=np.load('bin_track_x.npy')
# plane variants from book+ball fit
planes=[(0.01,35.0,1.713),(0.02,35.6,1.735),(0.03,36.1,1.757)]
def C_at(u,v,p,h,hc):
    U=np.array([0,-np.cos(p),-np.sin(p)])
    d=ray(u,v); t=(hc-h)/(U@d); return t*d
for tb,pd,h in planes:
    p=np.radians(pd)
    for hc in [0.11,0.13,0.15]:
        Cs=np.array([C_at(T[i,1],T[i,2],p,h,hc) for i in range(len(T))])
        steps=np.linalg.norm(np.diff(Cs,axis=0),axis=1)
        d10=np.linalg.norm(Cs[10]); 
        disp=np.linalg.norm(Cs[34]-Cs[10])
        # emulate labels: front surface range = |C|-delta, delta from t=0.4 ToF
        delta=d10-2.73
        P10=2.73*ray(T[10,1],T[10,2]); P34=(np.linalg.norm(Cs[34])-delta)*ray(T[34,1],T[34,2])
        v04=np.linalg.norm(Cs[11]-Cs[10])*25
        print('tb %.2f hc %.2f |C10| %.3f (ToF front 2.730 -> delta %.3f)  disp centres %.3f  disp emulated-front %.3f  v(0.4) fwd-diff %.3f m/s'%(tb,hc,d10,delta,disp,np.linalg.norm(P34-P10),v04))
p=np.radians(35.6); h=1.735
Cs=np.array([C_at(T[i,1],T[i,2],p,h,0.13) for i in range(len(T))])
steps=np.linalg.norm(np.diff(Cs,axis=0),axis=1)
print('per-video-frame 3D steps (cm):'); print(' '.join('%d:%.1f'%(i,100*s) for i,s in enumerate(steps)))
