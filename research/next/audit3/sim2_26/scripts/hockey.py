import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0126')
tr=[]
for i,f in enumerate(F):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    h,s,v=[hsv[...,k].astype(int) for k in range(3)]
    orange=((h>=8)&(h<=22)&(s>90)&(v>100)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(orange)
    if n<2: tr.append(None); continue
    k=1+np.argmax(st[1:,4]); x,y,w,hh,a=st[k]
    tr.append((i,cen[k][0],cen[k][1],w,hh,a))
for t in tr[::3]: print([round(float(v),1) for v in t] if t else None)
T=np.array([t for t in tr if t])
i=T[:,0];y=T[:,2]
m1=(i>=3)&(i<=38); m2=(i>=43)
p1=np.polyfit(i[m1],y[m1],1); p2=np.polyfit(i[m2],y[m2],1)
print('down px/f',p1,'up px/f',p2)
d=np.median(T[:,3]); print('median w',d,'median h',np.median(T[:,4]),'area eq d',np.sqrt(4*np.median(T[:,5])/np.pi))
print('dy diffs', np.round(np.diff(y),2))
