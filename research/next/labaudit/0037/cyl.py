"""Fit a vertical cylinder (centre on the table plane, radius R, height H) to four silhouette readings:
left/right image x at a given row, bottom-front y, top-back y. Camera f=711, pp=(640,360), plane normal n,
camera height h above the table. Solved by least squares over (cx, cz, R, H) in plane coordinates."""
import numpy as np
F=711.0; CX,CY=640.,360.
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0037/plane.npy')
e1=np.cross(n,[0,0,1.0]); e1/=np.linalg.norm(e1); e2=np.cross(e1,n); e2/=np.linalg.norm(e2)   # e2 ~ forward (depth)
def proj(X): return np.array([F*X[...,0]/X[...,2]+CX, F*X[...,1]/X[...,2]+CY]).T
def circle(c,R,y,h,N=720):
    th=np.linspace(0,2*np.pi,N,endpoint=False)
    O=-h*n  # foot of camera on plane (camera at origin, plane n.X=-h)
    P=O[None]+c[0]*e1[None]+c[1]*e2[None]+R*(np.cos(th)[:,None]*e1[None]+np.sin(th)[:,None]*e2[None])+y*n[None]
    return P
def silhouette(p,h,row_frac=0.5):
    cx,cz,R,H=p
    pts=np.vstack([circle((cx,cz),R,y,h) for y in np.linspace(0,H,25)])
    uv=proj(pts)
    bot=proj(circle((cx,cz),R,0,h)); top=proj(circle((cx,cz),R,H,h))
    return uv[:,0].min(),uv[:,0].max(),bot[:,1].max(),top[:,1].min()
def fit(obs,h,guess):
    res=lambda p: np.array(silhouette(p,h))-np.array(obs)
    p=np.array(guess,float)
    for it in range(60):
        f0=res(p); J=np.zeros((4,4))
        for j in range(4):
            dp=np.zeros(4); dp[j]=1e-5; J[:,j]=(res(p+dp)-f0)/1e-5
        step=np.linalg.lstsq(J,-f0,rcond=None)[0]
        p=p+0.7*step
        if np.abs(step).max()<1e-7: break
    return p, res(p)
if __name__=='__main__':
    O={'0037 jar':(443,500,484,408.5),'0040 jar':(481,543,497,416.5),'0037 tape':(521,592,473.5,430.5),'0040 tape':(551,628,484.5,437.5)}
    for h in (0.169,0.172,0.176,0.180):
        for k,obs in O.items():
            u=(obs[0]+obs[1])/2
            # initial guess: centre along the ray of the bottom-front pixel
            r=np.array([(u-CX)/F,(obs[2]-CY)/F,1]); Z=h/(-(n@r)); X=r*Z+(-h*n)*0  # point on plane
            Xp=X-(-h*n)
            g=[Xp@e1, Xp@e2+0.04, 0.04, 0.09]
            p,fun=fit(obs,h,g)
            print('h=%.3f %-10s diameter %.2f cm  height %.2f cm  centre depth %.3f  resid px %s'%(h,k,2*p[2]*100,p[3]*100,p[1],np.round(fun,2)))
