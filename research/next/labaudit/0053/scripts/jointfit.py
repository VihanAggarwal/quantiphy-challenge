import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
exec(open('scripts/wb62b.py').read().split('for n in (24,40,48):')[0])
C40,_,_=board_corners(40); C48,_,_=board_corners(48)
def nvec(a,b): return np.array([np.sin(b)*np.cos(a), np.cos(b)*np.cos(a), np.sin(a)])
pts=[('book',666.4,617.9,2.082,0.018,0.01),('cup',564.3,424.0,2.516,0.065,0.03),('ball',985.8,369.6,2.925,0.116,0.015),
     ('wb62',705.4,415.3,2.815,0.005,0.015),('bag62',837.3,329.1,3.307,0.01,0.015)]
def evaluate(f,pitch,roll,mode,verbose=False):
    dn=nvec(np.radians(pitch),np.radians(roll))
    def ray(u,v):
        d=np.array([(u-640)/f,(v-360)/f,1.0]); return d/np.linalg.norm(d)
    # whiteboard cost
    cw=0; E=[]
    for C in (C40,C48):
        Q=np.array([ray(u,v)/(ray(u,v)@dn) for u,v in C])
        for j in range(4):
            p=Q[j-1]-Q[j]; q=Q[(j+1)%4]-Q[j]
            cw+=(p@q/np.linalg.norm(p)/np.linalg.norm(q))**2/(np.radians(1.5)**2)
        E.append([np.linalg.norm(Q[(j+1)%4]-Q[j]) for j in range(4)])
    E=np.array(E); cw+=(((E[0]-E[1])/E.mean(0))**2).sum()/0.02**2
    # ToF heights
    X=[];Z=[];S=[]
    for nm,u,v,r,z,s in pts:
        d=np.array([(u-640)/f,(v-360)/f,1.0])
        p=r*d/np.linalg.norm(d) if mode=='range' else r*d
        if nm=='ball': p=p+0.116*d/np.linalg.norm(d); pb=p
        X.append(p);Z.append(z);S.append(s)
    X=np.array(X);Z=np.array(Z);S=np.array(S)
    h=X@dn+Z; w=1/S**2; H=(h*w).sum()/w.sum()
    ct=(((h-H)/S)**2).sum()
    # ball size: tangential 59.4 px
    db=np.linalg.norm(pb); th=np.arccos(ray(985.8,369.6)[2])
    pred=2*f*np.tan(np.arcsin(0.116/db))/np.cos(th)
    cb=((pred-59.4)/1.5)**2
    if verbose: print('   heights',np.round((H-X@dn)*100,1),'H %.3f ball px pred %.1f'%(H,pred))
    return cw,ct,cb,H
for mode in ('range','zdepth'):
    best=[]
    for f in range(660,861,10):
        for pitch in np.arange(30,44,0.5):
            for roll in np.arange(-14,-3,0.5):
                cw,ct,cb,H=evaluate(f,pitch,roll,mode)
                best.append((cw+ct+cb,cw,ct,cb,f,pitch,roll))
    best.sort()
    print(mode)
    for b in best[:4]: print('  total %.1f (wb %.1f tof %.1f ball %.1f) f %d pitch %.1f roll %.1f'%b)
    evaluate(*best[0][4:7],mode,verbose=True)
    # constrained to f=711
    b711=min([b for b in best if b[4]==710])
    print('  best at f=710: total %.1f (wb %.1f tof %.1f ball %.1f) f %d pitch %.1f roll %.1f'%b711)
    evaluate(*b711[4:7],mode,verbose=True)
