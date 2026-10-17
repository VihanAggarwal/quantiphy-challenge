from util import *
import sys
exec(open('qfall.py').read().split("np.set_printoptions")[0])
lo,hi=int(sys.argv[2]),int(sys.argv[3])
t=a[:,0]; sel=(t>=lo)&(t<=hi)
for name,col in [('cen',2),('top',3),('bot',4),('mid',None)]:
    y=a[sel,col] if col else (a[sel,3]+a[sel,4])/2
    p=np.polyfit(t[sel],y,2); acc=2*p[0]
    t0=-p[1]/(2*p[0])
    print(name,'acc px/f2 %.3f'%acc,'px/s2 %.0f'%(acc*576),'vertex frame %.2f'%t0,'rms %.2f'%np.std(y-np.polyval(p,t[sel])))
y=a[:,2]
d=np.diff(y)
print('backward diffs centroid', dict(zip(a[1:,0].astype(int),d.round(1))))
