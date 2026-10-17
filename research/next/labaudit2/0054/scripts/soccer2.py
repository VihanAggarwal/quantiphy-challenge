from common import *
import json
from fit_a import gd
def costh(u,v): return 1/np.sqrt(1+((u-CX)**2+(v-CY)**2)/F**2)
SB={int(k):v for k,v in json.load(open(OUT+'/soccer_b.json')).items()}
# ---- camera b: off-axis corrected size ranges anchored at stated 3.254 (surface) at video 48
R=0.10
def rb(k,s=None,c=None):
    o=SB[k]; c=c or o['c']; s=s or o['eb']
    o48=SB[48]; K=(3.254+R)*o48['eb']*costh(*o48['c'])
    return K/(s*costh(*c))
print('b ranges (centre): ' + ' '.join('%d:%.3f'%(k,rb(k)) for k in range(25,49,1)))
c24=(921.0,606.5)
for s24 in [62.5,63.0,64.0]:
    for s34 in [55.8,57.0]:
        r24=rb(24,s24,c24); r34=rb(34,s34)
        P24=(r24-R)*ray(*c24); P34=(r34-R)*ray(*SB[34]['c'])
        print(' b: s24=%.1f s34=%.1f r24=%.3f r34=%.3f disp(label-style surf)=%.3f  centres=%.3f'%(s24,s34,r24,r34,np.linalg.norm(P34-P24),np.linalg.norm(r34*ray(*SB[34]['c'])-r24*ray(*c24))))
# b soccer speed profile (centres)
P={k:rb(k)*ray(*SB[k]['c']) for k in range(25,49)}
print(' b speeds: '+' '.join('%d:%.2f'%(k,np.linalg.norm(P[k+1]-P[k])/(tcap(k+1)-tcap(k))) for k in range(25,48)))
# ---- camera a: floor plane
for H in [0.85,0.87,0.90]:
  for pitch in [0,1]:
    g=gd(pitch)
    def onfloor(u,v,h=R): d=ray(u,v); s=(H-h)/(d@g); return s*d
    for c24,c34 in [((153,610),(66.4,681.5)),((151.3,606.0),(66.4,688.0))]:
        P24=onfloor(*c24); P34=onfloor(*c34)
        L24=(np.linalg.norm(P24)-R)*ray(*c24); L34=(np.linalg.norm(P34)-R)*ray(*c34)
        print(' a H=%.2f pitch=%d c24=%s c34=%s: r24=%.3f r34=%.3f disp centres=%.3f label-style=%.3f'%(H,pitch,c24,c34,np.linalg.norm(P24),np.linalg.norm(P34),np.linalg.norm(P34-P24),np.linalg.norm(L34-L24)))
