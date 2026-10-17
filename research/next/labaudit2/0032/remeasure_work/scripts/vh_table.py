import numpy as np
f=711.; cx=640.; cy=360.
K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]]); Ki=np.linalg.inv(K)
def ray(u,v):
    d=Ki@np.array([u,v,1.]); return d/np.linalg.norm(d)
C=dict(FL=(462.94,482.41),FR=(963.71,494.87),BR=(851.13,428.32),BL=(574.72,424.04))
for vh in (340,344,346,349.5,352,354,356,358,362):
    lh=np.array([-0.00397,1.0,-(vh-0.00397*717.6)])
    n=K.T@lh; n/=np.linalg.norm(n)
    if n[1]<0: n=-n
    P={k:ray(*v)/(n@ray(*v)) for k,v in C.items()}  # unit height
    W=(np.linalg.norm(P['FR']-P['FL'])+np.linalg.norm(P['BR']-P['BL']))/2
    L=(np.linalg.norm(P['BL']-P['FL'])+np.linalg.norm(P['BR']-P['FR']))/2
    # orthogonality of table edges in 3D
    e1=P['FR']-P['FL']; e2=P['BL']-P['FL']
    ang=np.degrees(np.arccos(e1@e2/np.linalg.norm(e1)/np.linalg.norm(e2)))
    hpp=137.3*(n@ray(721.3,432.0))+2.0; hte=121.65*(n@ray(583.0,434.5))+3.35
    print('vh=%.1f  h_W(60.3)=%.2f h_L(76.0)=%.2f  W/L=%.3f corner angle %.1f | h_anchor pp %.2f tennis %.2f'%(vh,60.3/W,76.0/L,W/L,ang,hpp,hte))
