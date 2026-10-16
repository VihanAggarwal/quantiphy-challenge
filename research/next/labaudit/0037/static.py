"""Physical heights from the table plane (normal n from table.py; camera height h above the table top).
For a vertical object: Z of its front surface from the bottom-front contact pixel (on the plane); the top
pixel is back-projected at the front-surface Z (top-front edge) or at Z + depth extent (top-back edge)."""
import numpy as np
F=711.0; CX,CY=640.,360.
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0037/plane.npy')
def ray(u,v): return np.array([(u-CX)/F,(v-CY)/F,1.0])
def zplane(u,v,h,lift=0.0): r=ray(u,v); return (h-lift)/(-(n@r))
def height(u,v,Z,h): return h+Z*(n@ray(u,v))
objs={
 # name: (u, v_bottom_front, v_top, top_is_back, depth_extent_m)
 '0037 cup (top rim ~edge-on)':(776,503.5,376.5,False,0.0),
 '0037 jar top-front':(471,484,412.5,False,0.0),
 '0037 jar top-back':(471,484,408.5,True,0.072),
 '0037 tape axial top-front':(556,473.5,438,False,0.0),
 '0037 tape axial top-back':(556,473.5,430.5,True,0.104),
 '0037 poker apex vs blue foot':(686,499.5,416.5,False,0.0),
 '0037 poker apex vs red foot':(686,496,416.5,False,0.0),
 '0040 jar top-front':(512,497,422,False,0.0),
 '0040 jar top-back':(512,497,416.5,True,0.072),
 '0040 tape axial top-front':(590,484.5,445,False,0.0),
 '0040 tape axial top-back':(590,484.5,437.5,True,0.104),
}
for h in (0.169,0.172,0.176):
    print('h=%.3f'%h)
    for k,(u,vb,vt,back,ext) in objs.items():
        Z=zplane(u,vb,h); Zt=Z+ext
        print('   %-32s Zfront=%.3f range=%.3f  H=%.2f cm'%(k,Z,Z*np.linalg.norm(ray(u,vb)),height(u,vt,Zt,h)*100))
