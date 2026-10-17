# Exact sphere silhouette in the image (pinhole f, principal point 640,360): horizontal extent and vertical extent
import numpy as np
def silhouette(C, r, f=711., cx=640., cy=360., n=720):
    C=np.asarray(C,float); d=np.linalg.norm(C); u=C/d; a=np.arcsin(r/d)
    t=np.array([1.,0,0]) if abs(u[0])<0.9 else np.array([0,1.,0])
    e1=np.cross(u,t); e1/=np.linalg.norm(e1); e2=np.cross(u,e1)
    ph=np.linspace(0,2*np.pi,n,endpoint=False)
    q=np.cos(a)*u[None,:]+np.sin(a)*(np.cos(ph)[:,None]*e1+np.sin(ph)[:,None]*e2)
    x=f*q[:,0]/q[:,2]+cx; y=f*q[:,1]/q[:,2]+cy
    return x,y
def extents(C,r,f=711.):
    x,y=silhouette(C,r,f); return x.max()-x.min(), y.max()-y.min(), (x.max()+x.min())/2,(y.max()+y.min())/2, y.min(), y.max()
if __name__=='__main__':
    for C in [(0.155,0.139,1.357),(0.224,0.143,1.05)]:
        print(C, [round(v,2) for v in extents(C,0.02)], 'naive 2fr/Z', round(2*711*0.02/C[2],2))
