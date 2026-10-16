# Route 2: yoga ball radius from the floor plane (camera height from basketball / bin anchors), static frame 0
import numpy as np, sys
sys.path.insert(0,'scripts')
F=711.;CX=640;CY=360
def unit(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def rays(p,f=F):
    p=np.asarray(p,float); d=np.c_[(p[:,0]-CX)/f,(p[:,1]-CY)/f,np.ones(len(p))]; return d/np.linalg.norm(d,axis=1)[:,None]
# frame-0 silhouette extremes (o render, read from intensity profiles): left 551.5, right 673.5 @y510; top 443.5, bottom 572 @x612
pts=np.array([(551.5,510),(673.5,510),(612,443.5),(612,572)])
r=rays(pts)
w,*_=np.linalg.lstsq(r,np.ones(4),rcond=None); c=w/np.linalg.norm(w); a=np.arccos(1/np.linalg.norm(w))
print('t0 cone: centre ray ->(%.1f,%.1f) alpha=%.4f'%(CX+F*c[0]/c[2],CY+F*c[1]/c[2],a))
for phi in (0,0.5,1.0,1.5):
    p=np.radians(phi); down=np.array([0,np.cos(p),np.sin(p)])
    # camera height from anchors at this pitch
    bb=2.0525*unit(801.7,671.9); hb=bb@down+0.116
    binb=np.array([2.867*(728-CX)/F,2.867*(590.5-CY)/F,2.867]); hn=binb@down
    for h in (hb,hn):
        R=h/(1+(c@down)/np.sin(a))
        print('pitch %.1f h=%.3f -> R=%.4f diam %.1f cm'%(phi,h,R,200*R))
