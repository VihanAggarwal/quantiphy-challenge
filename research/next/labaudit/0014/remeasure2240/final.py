import numpy as np
f=711.0; cx,cy=640.,360.
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
Pt,Pb,e,h,n=np.load('model.npy')
# pooled centre track (mean of x/s renders, bg-difference centroids)
tr={0:(544.2,297.6),12:(545.8,329.2),13:(546.6,340.8),14:(547.6,354.0),15:(548.3,370.0),16:(549.5,389.2)}
src={12:13,13:14,14:15,15:16,16:17}   # our frame -> 25 fps source frame (one source frame dropped between our 11 and 12)
for r in [0.030,0.0325,0.035]:
    P0=Pb+r*n
    b3=lambda u,v:(n@P0)/(n@ray(u,v))*ray(u,v)
    P={k:b3(*v) for k,v in tr.items()}
    d=lambda a,b:np.linalg.norm(P[b]-P[a])
    # map stated range change 0->0.6 to our frame index
    dr=np.array([np.linalg.norm(P[k])-np.linalg.norm(P[0]) for k in [12,13,14,15,16]])
    fr=np.interp(1.7288-1.818,dr[::-1],[16,15,14,13,12])
    ks=[12,13,14,15,16]; t=np.array([src[k] for k in ks])/25.
    S=np.cumsum([0]+[d(a,b) for a,b in zip(ks[:-1],ks[1:])]); c=np.polyfit(t,S,2)
    print('r=%.3f  stated-dRange frame=%.2f  fwd 14->15 @25fps=%.1f  @24fps=%.1f  inst v(0.6)@25fps-timeline=%.1f  a=%.2f'%(
        r,fr,100*d(14,15)*25,100*d(14,15)*24,100*np.polyval(np.polyder(c),0.6),2*c[0]))
# route 2 (stated ranges only, our frame 14 = 0.6 s)
g=(1.7288-1.818)/(tr[14][1]-tr[0][1])
Q={k:(1.818+g*(v[1]-tr[0][1]))*ray(*v) for k,v in tr.items()}
print('route2 fwd 14->15 @25fps=%.1f @24fps=%.1f'%(100*np.linalg.norm(Q[15]-Q[14])*25,100*np.linalg.norm(Q[15]-Q[14])*24))
