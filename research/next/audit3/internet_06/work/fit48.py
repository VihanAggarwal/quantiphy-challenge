import numpy as np
d="""36 192.9 469.0 -5.6 -14.6
37 261.6 431.8 -6.0 -14.7
38 329.4 398.8 -6.4 -15.2
39 396.6 372.3 -6.7 -15.2
40 462.9 349.0 -6.9 -15.6
41 530.9 329.3 -7.3 -16.3
42 597.7 318.9 -7.5 -16.2
43 664.7 309.8 -7.6 -16.6
44 729.2 305.3 -7.8 -17.6
45 793.9 303.7 -8.2 -17.2
46 858.2 306.4 -8.4 -17.6
47 921.1 312.5 -8.8 -18.2
48 984.9 323.2 -9.2 -18.6
49 1048.4 337.6 -9.4 -18.3
50 1111.2 357.4 -9.9 -18.7
51 1174.1 379.5 -10.3 -19.4
52 1237.8 406.8 -10.4 -19.1
53 1302.0 438.4 -10.7 -19.6
54 1366.4 471.3 -11.3 -20.3
55 1432.3 508.8 -11.4 -20.8
56 1498.3 552.7 -11.7 -20.5
57 1562.7 602.3 -12.3 -21.1
58 1627.1 656.0 -12.8 -21.6
59 1691.8 713.2 -12.8 -21.9"""
A=np.array([[float(v) for v in l.split()] for l in d.splitlines()])
f=A[:,0]; t=f/30; x=A[:,1]-A[:,3]; y=A[:,2]-A[:,4]
# smooth drift by linear fit
for name,yy,xx in [('raw',A[:,2],A[:,1]),('comp',y,x)]:
  for sl in [slice(0,24),slice(2,22),slice(4,20)]:
    py=np.polyfit(t[sl],yy[sl],2); px=np.polyfit(t[sl],xx[sl],1)
    res=yy[sl]-np.polyval(py,t[sl])
    a=2*py[0]
    s=9.8/a  # m/px
    print(name,sl,'a px/s2',round(a,1),'m/px',round(s*1000,4),'mm/px','vx px/s',round(px[0],1),'vx m/s',round(px[0]*s,3),'rms',round(res.std(),2))
print('---')
for lo,hi in [(0,24),(2,24),(4,24),(0,22),(0,20),(3,23)]:
    sl=slice(lo,hi)
    py=np.polyfit(t[sl],y[sl],2); res=y[sl]-np.polyval(py,t[sl])
    print(int(f[lo]),int(f[hi-1]),'a',round(2*py[0],1),'rms',round(res.std(),2))
py=np.polyfit(t,y,2); print(np.round(y-np.polyval(py,t),1))
