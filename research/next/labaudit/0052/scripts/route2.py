# Route 2 for distances/bin height: floor-plane geometry (h, pitch) instead of each object's stated range
import numpy as np
F=711.;CX=640;CY=360
def ray(u,v): return np.array([(u-CX)/F,(v-CY)/F,1.0])
def unit(u,v): d=ray(u,v); return d/np.linalg.norm(d)
def at_height(u,v,h,phi,hz):
    p=np.radians(phi); down=np.array([0,np.cos(p),np.sin(p)]); d=ray(u,v); return (h-hz)/(d@down)*d
def surf(P,R):  # front-surface point from centre (for label-style comparisons)
    return P - R*P/np.linalg.norm(P)
for phi,h in ((0,0.925),(0.5,0.947),(1.0,0.967)):
    shoe=at_height(284,656.5,h,phi,0.04)
    bbc=at_height(801.7,671.9,h,phi,0.116); bb=surf(bbc,0.116)
    # bin: front face centre: front-bottom edge on floor at v=590.5 -> Z, then click (728,538) on that plane
    fb=at_height(728,590.5,h,phi,0.0); binp=ray(728,538)*fb[2]
    # yoga t0 centre at height R=0.274, surface point
    y0c=at_height(612.7,506.5,h,phi,0.274); y0=surf(y0c,0.274)
    # bin height: front-top rim at v=497.5 on the front face plane Z=fb[2]-0.02 (taper)
    p=np.radians(phi); down=np.array([0,np.cos(p),np.sin(p)])
    top=ray(728,497.5)*(fb[2]-0.02); H=fb@down-top@down
    topb=ray(728,485.5)*(fb[2]-0.02); Hb=fb@down-topb@down
    print('pitch %.1f h %.3f | ranges shoe %.3f bb %.3f bin %.3f yoga0 %.3f | bb-shoe %.3f bin-shoe %.3f bin-bb %.3f yoga0-shoe %.3f | bin H(front rim) %.1f cm, H(back-rim pixel) %.1f'%(
      phi,h,np.linalg.norm(shoe),np.linalg.norm(bb),np.linalg.norm(binp),np.linalg.norm(y0),
      np.linalg.norm(bb-shoe),np.linalg.norm(binp-shoe),np.linalg.norm(binp-bb),np.linalg.norm(y0-shoe),100*H,100*Hb))
