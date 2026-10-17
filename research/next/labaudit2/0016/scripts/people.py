# Distance between the two people: clicks back-projected at the stated ranges (near 0.843, far 2.372).
import numpy as np, itertools
f=711.; pp=np.array([640.,360.])
def ray(p): v=np.array([p[0]-pp[0],p[1]-pp[1],f]); return v/np.linalg.norm(v)
near={'head':(40,140),'neck':(30,280),'shoulder':(60,330),'chest':(90,420),'belly':(120,520),'hip':(150,600)}
far={'head':(1185,15),'chest':(1110,130),'torso':(1095,190),'hips':(1060,260),'knees':(1020,330),'feet':(965,405)}
vals=[]
for (kn,pn),(kf,pf) in itertools.product(near.items(),far.items()):
    d=np.linalg.norm(2.372*ray(pf)-0.843*ray(pn)); vals.append(d)
    print('%-8s %-6s %.1f cm'%(kn,kf,100*d))
print('range %.1f-%.1f  median %.1f'%(100*min(vals),100*max(vals),100*np.median(vals)))
