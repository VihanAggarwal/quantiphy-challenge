import json,numpy as np,sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0047/scripts')
from track import *
R=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0047/fit_x_711.json'))
def ray(p,f=F):
    v=np.array([(p[0]-CX)/f,(p[1]-CY)/f,1.0]); return v/np.linalg.norm(v)
def zray(p,f=F):
    return np.array([(p[0]-CX)/f,(p[1]-CY)/f,1.0])
r10,r15,rp=2.4985,1.4972,3.8300
print('--- displacement 1.0->1.5 and ball-person distance at 1.5 (label emulation, range model) ---')
persons={'centroid':(585,442),'torso':(585,420),'head':(580,375),'hips':(590,470)}
for n10 in [24]:
  for n15 in [35,36]:
    for mode in ['pc','circ','visible']:
        if mode=='pc': p10=R[str(n10)]['pc']; p15=R[str(n15)]['pc']
        elif mode=='circ': p10=(R[str(n10)]['cx'],R[str(n10)]['cy']); p15=(R[str(n15)]['cx'],R[str(n15)]['cy'])
        else:
            # centre of visible part (clip at y=719)
            p10=(R[str(n10)]['cx'],R[str(n10)]['cy'])
            cx,cy,r=R[str(n15)]['cx'],R[str(n15)]['cy'],R[str(n15)]['r']
            top=cy-r; bot=min(719,cy+r); p15=(cx,(top+bot)/2)
        A=r10*ray(p10); B=r15*ray(p15)
        disp=np.linalg.norm(B-A)
        Az=r10*zray(p10); Bz=r15*zray(p15)
        out=[f'n15={n15} {mode:8s} p15=({p15[0]:.0f},{p15[1]:.0f}) disp range {disp:.3f}  Z-model {np.linalg.norm(Bz-Az):.3f} |']
        for k,pp in persons.items():
            Pp=rp*ray(pp); Ppz=rp*zray(pp)
            out.append(f'{k}:{np.linalg.norm(Pp-B):.3f}/{np.linalg.norm(Ppz-Bz):.3f}')
        print(' '.join(out))
print('radial lower bound person-ball:',rp-r15)
