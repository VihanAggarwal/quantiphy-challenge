import numpy as np
f=711.0; cx,cy=640.,360.
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
tr={12:(545.8,329.2),13:(546.6,340.8),14:(547.6,354.0),15:(548.3,370.0),16:(549.5,389.2)}
for fr06 in [14.0,14.4,15.0]:
    y06=np.interp(fr06,list(tr),[v[1] for v in tr.values()]); x06=np.interp(fr06,list(tr),[v[0] for v in tr.values()])
    g=(1.7288-1.818)/(y06-297.6)
    P={k:(1.7288+g*(v[1]-y06))*ray(*v) for k,v in tr.items()}
    ks=sorted(P); inc=[np.linalg.norm(P[b]-P[a]) for a,b in zip(ks[:-1],ks[1:])]
    t=np.array(ks)/24.; S=np.cumsum([0]+inc)
    c=np.polyfit(t,S,2)
    print('t0.6 at frame %.1f: grad %.5f m/px; increments cm'%(fr06,g),np.round(100*np.array(inc),2),
          '| quad a=%.2f, v(0.6)@24fps=%.1f'%(2*c[0],100*np.polyval(np.polyder(c),0.6)),
          '| fwd-diff 14->15: v24=%.1f v25=%.1f'%(100*inc[2]*24,100*inc[2]*25))
