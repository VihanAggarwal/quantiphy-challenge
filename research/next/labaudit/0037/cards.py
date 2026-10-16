import numpy as np
F=711.0; CX,CY=640.,360.
n=np.load('plane.npy')
def ray(u,v): return np.array([(u-CX)/F,(v-CY)/F,1.0])
def onplane(u,v,h,lift=0.0):
    r=ray(u,v); return r*(-(h-lift)/(n@r))
cc=dict(TL=(528,529.4),TR=(617,535),BR=(606,551.2),BL=(510,543.8))
fc=dict(TL=(642.5,503.5),TR=(717.5,500),BR=(745.6,510.5),BL=(655,515.6))
for h in (0.169,0.172,0.176,0.180):
    Q={k:onplane(*v,h) for k,v in cc.items()}
    L=(np.linalg.norm(Q['TR']-Q['TL'])+np.linalg.norm(Q['BR']-Q['BL']))/2*100
    W=(np.linalg.norm(Q['BL']-Q['TL'])+np.linalg.norm(Q['BR']-Q['TR']))/2*100
    D=[np.linalg.norm(Q['BR']-Q['TL'])*100,np.linalg.norm(Q['TR']-Q['BL'])*100]
    c=np.mean(list(Q.values()),axis=0)
    Qf={k:onplane(*v,h) for k,v in fc.items()}
    Lf=[np.linalg.norm(Qf['TR']-Qf['TL'])*100,np.linalg.norm(Qf['BR']-Qf['BL'])*100]
    Wf=[np.linalg.norm(Qf['BL']-Qf['TL'])*100,np.linalg.norm(Qf['BR']-Qf['TR'])*100]
    print('h=%.3f credit card L=%.2f W=%.2f diag=%.1f/%.1f (true 8.56x5.40, diag 10.12) centre range=%.3f | flat card sides %s %s'%(h,L,W,*D,np.linalg.norm(c),np.round(Lf,2),np.round(Wf,2)))
