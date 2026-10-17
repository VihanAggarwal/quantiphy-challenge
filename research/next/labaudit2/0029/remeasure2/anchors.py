import numpy as np
def u(px,py,f=711.,cx=640.,cy=360.):
    v=np.array([(px-cx)/f,(py-cy)/f,1.]); return v/np.linalg.norm(v)
pix24={'c':(819.6,467.4),'s':(819.4,466.7),'x':(819.2,467.0),'circ':(818.7,465.3)}
pix30={'c':(708.1,439.1),'s':(707.7,438.2),'x':(707.8,438.5),'circ':(707.6,438.5)}
pix38={'c':(616.7,448.5),'x':(616.2,447.8),'circ':(616.3,447.6)}
for f in [690,711,730]:
  for k in pix24:
    P24=0.901*u(*pix24[k],f=f); P30=1.144*u(*pix30[k],f=f)
    k38='x' if k=='s' else k
    P38=1.027*u(*pix38[k38],f=f)
    print(f'f={f} {k:5s} dist(1.00->1.24)={100*np.linalg.norm(P30-P24):6.2f} cm  P24={100*P24.round(4)} P30={100*P30.round(4)}  dist(1.24->1.6)={100*np.linalg.norm(P38-P30):6.2f}')
# perturbation: click jitter 3px
rng=np.random.default_rng(0); ds=[]
for _ in range(2000):
    a=np.array(pix24['x'])+rng.normal(0,2.5,2); b=np.array(pix30['x'])+rng.normal(0,2.5,2)
    ds.append(100*np.linalg.norm(1.144*u(*b)-0.901*u(*a)))
print('jitter 2.5px: mean %.2f sd %.2f'%(np.mean(ds),np.std(ds)))
