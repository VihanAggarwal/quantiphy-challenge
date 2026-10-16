import numpy as np
F=711.;CX=640;CY=360
def unit(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
anchors={
 'bb centre (D=1.9365+0.116)':(2.0525*unit(801.7,671.9),0.116),
 'bin front-bottom (Z=2.867)':(np.array([2.867*(728-CX)/F,2.867*(590.5-CY)/F,2.867]),0.0),
 'yoga t0 centre (D0=3.284)':(3.284*unit(612,508),0.2744),
 'yoga t1 centre (D1=2.886)':(2.886*unit(572,544),0.2744),
 'shoe click (2.231, ~4cm up)':(2.231*unit(284,656.5),0.04),
}
for phi in (0,1,2,3,4,5,6):
    p=np.radians(phi)
    hs={k:P[1]*np.cos(p)+P[2]*np.sin(p)+hh for k,(P,hh) in anchors.items()}
    print('pitch %d: '%phi+' | '.join('%s %.3f'%(k.split(' (')[0],v) for k,v in hs.items()))
