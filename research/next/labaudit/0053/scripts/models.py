import numpy as np
def nvec(a,b): return np.array([np.sin(np.radians(b))*np.cos(np.radians(a)), np.cos(np.radians(b))*np.cos(np.radians(a)), np.sin(np.radians(a))])
class Model:
    def __init__(s,name,f,mode,pitch,roll,dn=None):
        s.name,s.f,s.mode=name,f,mode
        s.dn=nvec(pitch,roll) if dn is None else dn
        s.H=s.P(666.4,617.9,2.082)@s.dn+0.018
    def d(s,u,v): return np.array([(u-640)/s.f,(v-360)/s.f,1.0])
    def ray(s,u,v): d=s.d(u,v); return d/np.linalg.norm(d)
    def P(s,u,v,depth):
        d=s.d(u,v); return depth*d/np.linalg.norm(d) if s.mode=='range' else depth*d
    def fp(s,u,v,z=0.0):
        r=s.ray(u,v); return r*(s.H-z)/(r@s.dn)
    def depth_of(s,X):
        return np.linalg.norm(X) if s.mode=='range' else X[2]
M=[Model('M1 f711 range VPnormal',711,'range',None,None,dn=np.array([-0.14912498,0.81095659,0.56578367])),
   Model('M2 f780 zdepth fit',780,'zdepth',37.0,-9.0),
   Model('M3 f711 zdepth fit',711,'zdepth',39.5,-8.5),
   Model('M4 f760 zdepth fit',760,'zdepth',37.5,-9.0)]
