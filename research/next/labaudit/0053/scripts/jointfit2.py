import sys, numpy as np; sys.path.insert(0,'scripts')
exec(open('scripts/jointfit.py').read().split("for mode in ('range','zdepth'):")[0])
vpv=np.array([452.6,1379.1]); vpc=np.array([2194.6,121.2]); vpj=np.array([219.5,-241.0])
def vpcost(f,pitch,roll):
    dn=nvec(np.radians(pitch),np.radians(roll))
    def r(p):
        d=np.array([(p[0]-640)/f,(p[1]-360)/f,1.0]); return d/np.linalg.norm(d)
    c=0
    c+=(np.degrees(np.arccos(np.clip(r(vpv)@dn,-1,1)))/1.5)**2
    c+=(np.degrees(np.arcsin(r(vpc)@dn))/2.0)**2
    c+=(np.degrees(np.arcsin(r(vpj)@dn))/2.0)**2
    return c
for mode in ('range','zdepth'):
    best=[]
    for f in range(680,841,10):
        for pitch in np.arange(32,42,0.5):
            for roll in np.arange(-13,-5,0.5):
                cw,ct,cb,H=evaluate(f,pitch,roll,mode)
                cv=vpcost(f,pitch,roll)
                best.append((cw+ct+cb+cv,cw,ct,cb,cv,f,pitch,roll))
    best.sort()
    print(mode)
    for b in best[:5]: print('  total %.1f (wb %.1f tof %.1f ball %.1f vp %.1f) f %d pitch %.1f roll %.1f'%b)
    for F0 in (710,750,780):
        b=min([x for x in best if x[5]==F0]); print('  best at f=%d: total %.1f (wb %.1f tof %.1f ball %.1f vp %.1f) pitch %.1f roll %.1f'%(F0,b[0],b[1],b[2],b[3],b[4],b[6],b[7]))
