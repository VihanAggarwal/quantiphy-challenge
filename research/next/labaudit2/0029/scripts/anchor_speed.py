# physical approach speed at t=1.0 from the stated anchors only: chord from the n25 ball centre to the contact point
# (ball centre at the stated n31 range, pixel interpolated to the contact time), divided by the time to contact
import numpy as np, json
from geom import ray
f=711.
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
def unit(p): d=ray(*p,f); return d/np.linalg.norm(d)
P24=(0.901+0.0335)*unit(uv[24])
for kc in [29.3,29.5,29.7]:
    a=kc-29; pc=(1-a)*uv[29]+a*uv[30]
    Pc=(1.144+0.0335)*unit(pc)
    d=np.linalg.norm(Pc-P24); steps=(kc+1)-25   # capture n = video k + 1 here
    print('contact at video %.1f: chord %.1f cm over %.1f steps -> %.0f cm/s'%(kc,100*d,steps,100*d/steps*25))
