import numpy as np
F=711.;CX=640.;CY=360.
def ray(u,v):
    d=np.array([(u-CX)/F,(v-CY)/F,1.]); return d/np.linalg.norm(d)
T=1.201*ray(587,357); B=0.9555*ray(585,481)
Ls=np.linalg.norm(T-B); print('0023 slope line length %.1f cm'%(Ls*100))
u_al=(T-B)/Ls
# slope normal: perpendicular to u_al and to horizontal across direction (camera x approx)
ex=np.array([1.,0,0]); nrm=np.cross(ex,u_al); nrm/=np.linalg.norm(nrm)
if nrm@(-(T+B)/2)<0: nrm=-nrm
def along_at_v(v,h=0.,u=587):
    # point on plane through B with normal nrm offset h, on ray(u,v)
    d=ray(u,v); s=(nrm@B+h)/(nrm@d); X=s*d; return (X-B)@u_al*100, np.linalg.norm(X)
print('incline normal',nrm.round(3))
for v in [349,357,378,388]:
    print('v',v,'h0 along %.1f range %.3f'%along_at_v(v),' h1.46 along %.1f'%along_at_v(v,0.0146)[0])
print('--- per-column silhouette route, 0023 (top sil 349.8, pages bottom 388) ---')
for H in [1.2,1.46,1.8]:
    for (vt,vb) in [(349.8,388.0),(349.3,387.5),(350.3,388.5)]:
        a_up=along_at_v(vt,H/100)[0]; a_pb=along_at_v(vb,0)[0]
        print('H %.2f vt %.1f vb %.1f: up %.1f pages-bottom %.1f W %.2f'%(H,vt,vb,a_up,a_pb,a_up-a_pb))
# sensitivity to stated depths (+-1.5 cm each)
for dT in [-0.015,0,0.015]:
    for dB in [-0.015,0,0.015]:
        T2=(1.201+dT)*ray(587,357); B2=(0.9555+dB)*ray(585,481)
        u2=(T2-B2)/np.linalg.norm(T2-B2); n2=np.cross(np.array([1.,0,0]),u2); n2/=np.linalg.norm(n2)
        if n2@(-(T2+B2)/2)<0: n2=-n2
        def al(v,h):
            d=ray(587,v); s=(n2@B2+h)/(n2@d); X=s*d; return (X-B2)@u2*100
        print('dT %+.3f dB %+.3f: slope len %.1f  W %.2f'%(dT,dB,np.linalg.norm(T2-B2)*100, al(349.8,0.0146)-al(388,0)))
