# A3 shared camera (0202/0205/0206/0209): pitched camera, roll 0, principal point at image centre.
import numpy as np
CX,CY=1062.0,540.0
def lineinter(p1,p2,p3,p4):
    p1,p2,p3,p4=[np.array([*p,1.0]) for p in (p1,p2,p3,p4)]
    l1=np.cross(p1,p2); l2=np.cross(p3,p4); v=np.cross(l1,l2); return v[:2]/v[2]
# desk top-surface corners (agent 0209 silhouette/edge fits; same pixels in 0202 notes)
N=(698.9,877.2); R=(1979.8,640.3); L=(472.5,685.5); F=(1599.2,525.3)
VPl=lineinter(N,R,L,F); VPs=lineinter(N,L,R,F)
yh=(VPl[1]+VPs[1])/2
f_vp=np.sqrt(-((VPl[0]-CX)*(VPs[0]-CX)) - (yh-CY)**2)
def setup(f, theta_deg=None):
    th=np.arctan((CY-yh)/f) if theta_deg is None else np.radians(theta_deg)
    right=np.array([1,0,0.]); fwd=np.array([0,np.cos(th),-np.sin(th)]); down=np.array([0,-np.sin(th),-np.cos(th)])
    M=np.stack([right,down,fwd],axis=1)  # world = M @ cam
    return th,M
def ray(u,v,f,M):
    d=M@np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def onplane(u,v,f,M,h):
    d=ray(u,v,f,M); t=-h/d[2]; return t*d
if __name__=='__main__':
    print('VP long',VPl,'VP short',VPs,'horizon y %.1f'%yh,'f from VPs %.1f'%f_vp)
    for f in (2630.,2650.,2670.):
        th,M=setup(f)
        # plane height from near corner range 3.593 and far-right range 5.009
        hN=-3.593*ray(*N,f,M)[2]; hR=-5.009*ray(*R,f,M)[2]
        PN=3.593*ray(*N,f,M); PR=5.009*ray(*R,f,M)
        print('f=%.0f pitch=%.2f  h from N %.4f  from R %.4f  |N-R| by ranges %.4f'%(f,np.degrees(th),hN,hR,np.linalg.norm(PN-PR)))
        h=(hN+hR)/2
        P={k:onplane(*p,f,M,h) for k,p in dict(N=N,R=R,L=L,F=F).items()}
        print('   on-plane: NR %.3f LF %.3f NL %.3f RF %.3f'%(np.linalg.norm(P['N']-P['R']),np.linalg.norm(P['L']-P['F']),np.linalg.norm(P['N']-P['L']),np.linalg.norm(P['R']-P['F'])))
        # gun range check: gun origin pixel ~ (1430,625)
        g=onplane(1430,625,f,M,h); print('   gun pixel (1430,625) on plane range %.3f (given 4.704)'%np.linalg.norm(g))
        ex=(P['R']-P['N'])/np.linalg.norm(P['R']-P['N']); ey=(P['L']-P['N'])/np.linalg.norm(P['L']-P['N'])
        print('   desk axes angle %.2f deg'%np.degrees(np.arccos(ex@ey)))
        def uv(p): q=onplane(*p,f,M,h)-P['N']; return np.array([q@ex,q@ey])
        Lc=(1320.,624.5); Nc=(1362.,643.5); Rv=(1409.,634.5)
        a,b,c=uv(Lc),uv(Nc),uv(Rv)
        print('   letter L uv',a.round(3),'N uv',b.round(3),'Rvis uv',c.round(3))
        print('   |L-N| %.3f  |N-Rvis| %.3f'%(np.linalg.norm(a-b),np.linalg.norm(c-b)))
