from util import *
fr=frames('simulation_0262')
rows=[]
for i,f in fr:
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=(((hsv[...,0]<8)|(hsv[...,0]>172))&(hsv[...,1]>150)&(hsv[...,2]>80)).astype(np.uint8)
    ys,xs=np.where(m)
    if len(ys)<200: continue
    rows.append((i,ys.min(),ys.max(),ys.mean(),xs.min(),xs.max(),len(ys)))
a=np.array(rows,float)
np.set_printoptions(suppress=True,linewidth=150,precision=2)
print(a[:22])
t=a[:,0]
for lo,hi in [(7,17),(6,18),(8,16)]:
  sel=(t>=lo)&(t<=hi)
  for name,col in [('top',1),('bot',2),('mean',3)]:
    p=np.polyfit(t[sel],a[sel,col],2); print(lo,hi,name,'acc %.3f'%(2*p[0]),'vertex %.2f'%(-p[1]/(2*p[0])),'rms %.2f'%np.std(a[sel,col]-np.polyval(p,t[sel])))
d=np.diff(a[:,2]); print('bot diffs',dict(zip(a[1:,0].astype(int),d.round(1))))
d=np.diff(a[:,1]); print('top diffs',dict(zip(a[1:,0].astype(int),d.round(1))))
