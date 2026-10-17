from tm import track
import numpy as np
cfg=[('0257',9,(1040,1094,305,375),(990,1150),range(0,14)),
     ('0258',12,(986,1064,468,488),(960,1100),range(6,16)),
     ('0259',9,(830,882,308,386),(780,940),range(0,15)),
     ('0260',10,(1212,1288,272,338),(1150,1350),range(6,16))]
for v,tf,box,(x0,x1),frs in cfg:
    R=track(v,tf,box,x0,x1,frs)
    t=np.array([r[0] for r in R]);y=np.array([r[2] for r in R])
    d1=np.diff(y); d2=np.diff(d1)
    print(v,'v(px/f):',np.round(d1,2))
    print(v,'a(px/f2):',np.round(d2,2))
    # linear fit of d1 vs mid-time
    tm=(t[1:]+t[:-1])/2
    p=np.polyfit(tm,d1,1); print(v,'slope of v: %.4f  v-intercept zero at t=%.3f'%(p[0],-p[1]/p[0]))
    # ratio of v at matched times to predicted 6.9*(t-t0)
