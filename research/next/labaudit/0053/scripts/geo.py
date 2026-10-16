import numpy as np
F=711.0; CX=640.0; CY=360.0
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def P(u,v,r,f=F): return r*ray(u,v,f)
R={'bin':2.73,'cup':2.516,'book':2.082,'bb':2.925}
C={'book':(666.4,617.9),'cup':(564.3,424.0),'bb':(985.8,369.6),'bin':(797.7,379.5)}
VP_V=(452.6,1379.1)
def down_from_vp(vp,f=F):
    d=np.array([(vp[0]-CX)/f,(vp[1]-CY)/f,1.0]); return d/np.linalg.norm(d)
DOWN_ROLL=down_from_vp(VP_V)
DOWN_NOROLL=np.array([0,np.cos(np.radians(34.5)),np.sin(np.radians(34.5))])
def floor_pt(u,v,H,down,z=0.0,f=F):
    r=ray(u,v,f); t=(H-z)/(r@down); return t*r
