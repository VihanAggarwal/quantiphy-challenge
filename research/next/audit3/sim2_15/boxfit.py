from util import *
import sys
v=sys.argv[1]; f0,f1=int(sys.argv[2]),int(sys.argv[3]); prior_a=float(sys.argv[4])
fr=frames(v); st=np.stack([f.astype(np.int16) for f in fr]); bg=np.median(st,axis=0)
C=[]
for i in range(len(fr)):
    d=(np.abs(st[i]-bg).max(axis=2)>30).astype(np.uint8)
    d=cv2.morphologyEx(d,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nn,lab,stats,cen=cv2.connectedComponentsWithStats(d)
    k=1+np.argmax(stats[1:,4]); ys,xs=np.nonzero(lab==k); C.append((xs.mean(),ys.mean()))
C=np.array(C)
# fall phase frames 0..7
t=np.arange(0,8); p=np.polyfit(t,C[:8,1],2); afall=2*p[0]*576
print('fall a px/s2 %.0f -> px/m %.1f'%(afall,afall/9.81))
th=np.deg2rad(28.5); u=np.array([np.cos(th),np.sin(th)])
idx=np.arange(f0,f1+1); s=C[idx]@u
p=np.polyfit(idx,s,2); a=2*p[0]*576; res=s-np.polyval(p,idx)
print('slide a px/s2 %.1f rms %.2f'%(a,res.std()))
for scale_name,ppm in [('prior',a/prior_a),('grav',afall/9.81)]:
    for n in [24,36]:
        vpx=(np.polyval(p,n)-np.polyval(p,n-1))*24
        # also raw 2D speed from centroid
        raw=np.linalg.norm(C[n]-C[n-1])*24
        print(scale_name,'ppm %.1f'%ppm,'frame',n,'fit v %.3f m/s'%(vpx/ppm),'raw %.3f'%(raw/ppm))
# free fall acc 0-0.3: v at frame 7 backward
for n in [7]:
    vb=np.linalg.norm(C[n]-C[n-1])*24
    print('v(f7) raw',vb/(afall/9.81),'/0.3=',vb/(afall/9.81)/0.3)
