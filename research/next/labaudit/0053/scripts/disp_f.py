import numpy as np
vpv=np.array([452.6,1379.1])
def ray(u,v,f):
    d=np.array([(u-640)/f,(v-360)/f,1.0]); return d/np.linalg.norm(d)
c10=(797.7,379.5); c34=(614.1,268.0)
t10=(782.3,419.5); t34=(595.5,299.3)
for f in (711,730,760,800):
    dn=ray(*vpv,f); H=2.082*ray(666.4,617.9,f)@dn+0.018
    P10=2.73*ray(*c10,f); z=H-P10@dn
    r34=(H-z)/(ray(*c34,f)@dn); P34=r34*ray(*c34,f)
    dA=np.linalg.norm(P34-P10)
    # size route r34
    out=[]
    for k in (1.124,1.150):
        out.append(np.linalg.norm(2.73*k*ray(*c34,f)-P10))
    # tab route z=0..0.03
    def fp(p,zz):
        r=ray(*p,f); return r*(H-zz)/(r@dn)
    dT=[np.linalg.norm(fp(t34,zz)-fp(t10,zz)) for zz in (0.0,0.03)]
    # same-range artefact
    dS=np.linalg.norm(2.73*ray(*c34,f)-P10)
    print(f,'H %.3f binz %.3f r34 %.3f | floor-click %.3f | size %.3f-%.3f | tab %.3f-%.3f | same-range %.3f'%(H,z,r34,dA,out[0],out[1],dT[1],dT[0],dS))
